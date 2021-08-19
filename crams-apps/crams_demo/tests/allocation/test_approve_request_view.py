import json
import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import routers

from crams_allocation.models import Request
from crams_allocation.test_utils import UnitTestCase
from crams.constants import db
from crams.utils.crams_utils import get_random_string

class ApproveRequestViewTest(UnitTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.client = self.auth_client(user=self.approver_user)
        self.prov_client = self.auth_client(user=self.provisioner_user)

    def test_approve_request_list_submit_extended_view(self):
        # check submitted and extended projects waiting for approval
        url = '/approve_list'
        response = self.client.get(url)
        assert response.status_code == 200
        # check admin user is correct
        assert response.data['user']['email'] == self.approver_user.email
        
        # check that all requests in are code X(Extension) or E(Submit)
        valid_codes = [db.REQUEST_STATUS_SUBMITTED, db.REQUEST_STATUS_UPDATE_OR_EXTEND]
        projects = response.data['projects']
        for prj in projects:
            for req in prj['requests']:
                if req['request_status']['code'] not in valid_codes:
                    assert False
    
    def test_approve_request_list_approved_view(self):
        # check projects already approved
        url = '/approve_list?req_status=approved'
        response = self.client.get(url)
        assert response.status_code == 200
        # check admin user is correct
        assert response.data['user']['email'] == self.approver_user.email
        
        # check that all request codes are A(Approved)
        projects = response.data['projects']
        for prj in projects:
            for req in prj['requests']:
                if req['request_status']['code'] != db.REQUEST_STATUS_APPROVED:
                    assert False

    def test_approve_request_list_provisioned_view(self):
        # check projects that are active/provisioned
        url = '/approve_list?req_status=active'
        response = self.prov_client.get(url)
        assert response.status_code == 200
        # check admin user is correct
        assert response.data['user']['email'] == self.provisioner_user.email
        
        # check that all request codes are P(Provisioned)
        projects = response.data['projects']
        for prj in projects:
            for req in prj['requests']:
                if req['request_status']['code'] != db.REQUEST_STATUS_PROVISIONED:
                    assert False
        
        
    def test_approve_request_detail_view(self):
        req_id = self.prj_submit.requests.all().first().id
        url = reverse('approve-request-detail', args=[req_id])
        response = self.client.get(url)
        assert response.status_code == 200

        # check project
        assert response.data['project']['title'] == self.prj_submit.title
        # check request
        req = self.prj_submit.requests.all().first()
        assert response.data['request_status']['code'] == req.request_status.code 

        # check storage request quota
        sp_req = req.storage_requests.all().first()
        assert response.data['storage_requests'][0]['requested_quota_change'] == sp_req.requested_quota_change
        assert response.data['storage_requests'][0]['requested_quota_total'] == sp_req.requested_quota_total

    def _test_approve_request_approval_view(self, project):
        # set up the payload
        req = project.requests.all().first()
        sp_req = req.storage_requests.all().first()
        payload = self.get_empty_approve_json_payload()
        payload['funding_scheme']['id'] = self.funding_scheme.id
        payload['funding_scheme']['funding_scheme'] = self.funding_scheme.funding_scheme
        payload['approval_notes'] = get_random_string(50)
        payload['storage_requests'][0]['id'] = sp_req.id
        payload['storage_requests'][0]['storage_product']['id'] = self.storage_prod.id
        payload['storage_requests'][0]['storage_product']['name'] = self.storage_prod.name
        payload['storage_requests'][0]['storage_product']['storage_type']['id'] = self.storage_type.id
        payload['storage_requests'][0]['storage_product']['storage_type']['storage_type'] = self.storage_type.storage_type
        payload['storage_requests'][0]['requested_quota_change'] = sp_req.requested_quota_change
        payload['storage_requests'][0]['requested_quota_total'] = sp_req.requested_quota_total
        payload['storage_requests'][0]['approved_quota_change'] = sp_req.requested_quota_change
        payload['storage_requests'][0]['approved_quota_total'] = sp_req.requested_quota_total
        
        url = reverse('approve-request-detail', args=[req.id])
        response = self.client.put(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 200
        
        appr_req = Request.objects.get(pk=response.data['id'])
        sub_req = Request.objects.filter(current_request=appr_req).first()
        # check submit request parent id matches new approved request id
        assert sub_req
        # check request has been approved
        assert appr_req.request_status.code == db.REQUEST_STATUS_APPROVED
        # check approved quota set
        appr_sp_req = appr_req.storage_requests.all().first()
        assert appr_sp_req.approved_quota_change == sp_req.requested_quota_change
        assert appr_sp_req.approved_quota_total == sp_req.requested_quota_total
        # check approval notes
        assert appr_req.approval_notes == payload['approval_notes']

    def test_approve_request_approval_view_submission(self):
        # test a new submitted project request for approval
        self._test_approve_request_approval_view(self.prj_submit)

    def test_approve_request_approval_view_extension(self):
        # test an existing provisioned project request that has its quota extended
        self._test_approve_request_approval_view(self.prj_alloc_ext)