import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import routers

from crams_allocation.test_utils import UnitTestCase


class ProjectRequestViewTest(UnitTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.app_client = self.auth_client(user=self.app_user)
        self.admin_client = self.auth_client(user=self.admin_user)

    def test_project_request_view_list(self):
        url = reverse("project-request-list")
        response = self.app_client.get(url)
        assert response.status_code == 200

        # check for submission project
        sub_prj = next((x for x in response.data if x['id'] == self.prj_submit.id), None)
        assert sub_prj['title'] == self.prj_submit.title
        assert sub_prj['requests'][0]['request_status']['code'] == self.prj_submit.requests.all().first().request_status.code

        # check for approved project
        appr_prj = next((x for x in response.data if x['id'] == self.prj_approved.id), None)
        assert appr_prj['title'] == self.prj_approved.title
        assert appr_prj['requests'][0]['request_status']['code'] == self.prj_approved.requests.all().first().request_status.code

        # check for provisioned project
        prov_prj = next((x for x in response.data if x['id'] == self.prj_prov.id), None)
        assert prov_prj['title'] == self.prj_prov.title
        assert prov_prj['requests'][0]['request_status']['code'] == self.prj_prov.requests.all().first().request_status.code

    def test_project_request_view_detail(self):
        url = reverse("project-request-detail", args=[self.prj_prov.requests.all().first().id])
        response = self.app_client.get(url) 
        assert response.status_code == 200
        
        prov_prj = response.data
        assert prov_prj['id'] == self.prj_prov.id
        assert prov_prj['title'] == self.prj_prov.title
        assert prov_prj['requests'][0]['id'] == self.prj_prov.requests.all().first().id
        assert prov_prj['requests'][0]['request_status']['code'] == self.prj_prov.requests.all().first().request_status.code