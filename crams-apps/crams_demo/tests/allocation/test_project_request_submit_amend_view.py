import json
import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import routers

from crams_allocation.test_utils import UnitTestCase
from crams_collection.models import Project
from crams.utils.crams_utils import get_random_string


class ProjectRequestSubmitAmmendViewTest(UnitTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.client = self.auth_client(user=self.app_user)

    def test_project_request_submit(self):
        payload = self.get_submit_json_payload()
        url = "/project_request/"
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 201
        # check the newly created project
        project_id = response.data['id']
        project = Project.objects.get(pk=project_id)
        request = project.requests.all().first()
        storage_request = request.storage_requests.all().first()
        assert project.title == payload['title']
        assert (request.request_status.code == 
            payload['requests'][0]['request_status']['code'])
        assert (storage_request.storage_product.id == 
            payload['requests'][0]['storage_requests'][0]['storage_product']['id'])
        assert (storage_request.current_quota == 
            payload['requests'][0]['storage_requests'][0]['current_quota'])
        assert (storage_request.current_quota == 
            payload['requests'][0]['storage_requests'][0]['current_quota'])
        assert (storage_request.requested_quota_change == 
            payload['requests'][0]['storage_requests'][0]['requested_quota_change'])

    def test_project_request_submit_amend(self):
        url = "/project_request/"
        # using the submit project request id fetch the payload
        sub_request_id = self.prj_submit.requests.all().first().id
        response = self.client.get(url + "?request_id=" + str(sub_request_id))
        assert response.status_code == 200
        payload = response.data[0]
        # modifiy the project title
        new_title = get_random_string(25)
        payload['title'] = new_title
        # change the quota
        quota_change = 20
        payload['requests'][0]['storage_requests'][0]['requested_quota_change'] = quota_change
        payload['requests'][0]['storage_requests'][0]['requested_quota_total'] = quota_change
        url = url + str(payload['id']) + '/'
        response = self.client.put(url, data=json.dumps(payload), 
            content_type="application/json")
        assert response.status_code == 200
        # get the new id and fetch allocation from db
        new_prj_id = response.data['id']
        new_prj = Project.objects.get(pk=new_prj_id)
        # check title changed
        assert new_prj.title == new_title
        # check quota changed
        sp_req = new_prj.requests.all().first().storage_requests.all().first()
        assert sp_req.requested_quota_change == quota_change
        assert sp_req.requested_quota_total == quota_change

    def test_project_request_draft_submit(self):
        payload = self.get_empty_draft_json_payload()
        url = "/project_request/?draft"
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 201
        # check the newly created project
        project_id = response.data['id']
        project = Project.objects.get(pk=project_id)
        request = project.requests.all().first()
        assert project.title == payload['title']
        assert (request.request_status.code == 
            payload['requests'][0]['request_status']['code'])

    def test_project_request_draft_amend(self):
        # using the draft project request id fetch the payload
        sub_request_id = self.prj_draft.requests.all().first().id
        url = "/project_request/"
        response = self.client.get(url + "?request_id=" + str(sub_request_id))
        assert response.status_code == 200
        payload = response.data[0]
         # modifiy the project title
        new_title = get_random_string(25)
        payload['title'] = new_title
        url = url + str(payload['id']) + '/?draft'
        response = self.client.put(url, data=json.dumps(payload), 
            content_type="application/json")
        assert response.status_code == 200
        # get the new id and fetch allocation from db
        new_prj_id = response.data['id']
        new_prj = Project.objects.get(pk=new_prj_id)
        # check title changed
        assert new_prj.title == new_title
