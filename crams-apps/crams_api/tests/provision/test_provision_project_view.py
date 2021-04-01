import json
import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import routers

from crams.constants import db
from crams.utils.crams_utils import get_random_string
from crams_allocation.test_utils import UnitTestCase
from crams_allocation.models import Request
from crams_provision.test_utils import UnitTestCase as ProvTestCase

class ProvisionProjectViewTest(UnitTestCase, ProvTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.client = self.auth_client(user=self.provisioner_user)

    def test_provision_project_view_list(self):
        url = "/provision_project/list/"
        response = self.client.get(url)
        assert response.status_code == 200
        # check all projects in the list are approved status
        for prj in response.data:
            for req in prj['requests']:
                if req['request_status']['code'] != db.REQUEST_STATUS_APPROVED:
                    assert False

        # check the existing approved project in the list
        appr_prj = next((x for x in response.data if x['id'] == self.prj_approved.id), None)
        assert appr_prj

    def test_provision_project_view_detail(self):
        url = "/provision_project/list/{}/".format(self.prj_approved.id)
        response = self.client.get(url)
        assert response.status_code == 200
        
        # check details of approved projected
        assert response.data['id'] == self.prj_approved.id
        assert response.data['requests'][0]['request_status']['code'] == db.REQUEST_STATUS_APPROVED
        sp_req = self.prj_approved.requests.all().first().storage_requests.all().first()
        assert response.data['requests'][0]['storage_requests'][0]['current_quota'] == sp_req.current_quota
        assert response.data['requests'][0]['storage_requests'][0]['approved_quota_change'] == sp_req.approved_quota_change
        assert response.data['requests'][0]['storage_requests'][0]['approved_quota_total'] == sp_req.approved_quota_total

    def test_provision_project_view_update(self):
        # get request and project and set up the payload
        payload = self.get_provision_json_payload(self.prj_approved)
        url = "/provision_project/update/"
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 201
        # check the approve request has been updated and get the new prov req
        req_id = self.prj_approved.requests.all().first().id
        appr_req = Request.objects.get(pk=req_id) # fetch the updated req
        prov_req = Request.objects.get(pk=response.data['requests'][0]['id'])
        assert appr_req.current_request == prov_req
        assert prov_req.request_status.code == db.REQUEST_STATUS_PROVISIONED
