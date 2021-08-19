import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import routers

from crams_allocation.test_utils import UnitTestCase


class ProjectListViewTest(UnitTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.app_client = self.auth_client(user=self.app_user)
        self.faculty_client = self.auth_client(user=self.faculty_user)
        self.admin_client = self.auth_client(user=self.admin_user)

    def test_project_list(self):
        url = "/allocation_list/"
        response = self.app_client.get(url)
        assert response.status_code == 200
        
        # check for submission project
        sub_prj = next((x for x in response.data if x['id'] == self.prj_submit.id), None)
        assert sub_prj['title'] == self.prj_submit.title
        sub_req = self.prj_submit.requests.all().first()
        assert sub_prj['requests'][0]['request_status']['code'] == sub_req.request_status.code
        
        # check for approved project
        appr_prj = next((x for x in response.data if x['id'] == self.prj_approved.id), None)
        assert appr_prj['title'] == self.prj_approved.title
        appr_req = self.prj_approved.requests.all().first()
        assert appr_prj['requests'][0]['request_status']['code'] == appr_req.request_status.code

        # check for provisioned project
        prov_prj = next((x for x in response.data if x['id'] == self.prj_prov.id), None)
        assert prov_prj['title'] == self.prj_prov.title
        prov_req = self.prj_prov.requests.all().first()
        assert prov_prj['requests'][0]['request_status']['code'] == prov_req.request_status.code

    def test_project_list_new_user(self):
        url = reverse("project-list")
        client = self.auth_client()
        response = client.get(url)
        assert response.status_code == 200
        # check user should have no projects
        assert len(response.data) == 0
        
    def test_project_list_admin(self):
        url = reverse("project-admin-list")
        response = self.admin_client.get(url)
        assert response.status_code == 200
        
        # check for submission project
        sub_prj = next((x for x in response.data if x['project']['id'] == self.prj_submit.id), None)
        assert sub_prj['project']['title'] == self.prj_submit.title

        # check for approved project
        appr_prj = next((x for x in response.data if x['project']['id'] == self.prj_approved.id), None)
        assert appr_prj['project']['title'] == self.prj_approved.title

        # check for provisioned project
        prov_prj = next((x for x in response.data if x['project']['id'] == self.prj_prov.id), None)
        assert prov_prj['project']['title'] == self.prj_prov.title
    
    def test_project_list_department(self):
        url = "/project_request_list/department/"
        response = self.admin_client.get(url)
        assert response.status_code == 200
    
    def test_project_list_faculty(self):
        url = "/project_request_list/faculty/"
        response = self.faculty_client.get(url)
        assert response.status_code == 200
        # check for submission project
        sub_prj = next((x for x in response.data['projects'] if x['id'] == self.prj_submit.id), None)
        assert sub_prj['title'] == self.prj_submit.title

        # check for approved project
        appr_prj = next((x for x in response.data['projects'] if x['id'] == self.prj_approved.id), None)
        assert appr_prj['title'] == self.prj_approved.title

        # check for provisioned project
        prov_prj = next((x for x in response.data['projects'] if x['id'] == self.prj_prov.id), None)
        assert prov_prj['title'] == self.prj_prov.title

    def test_project_list_organisation(self):
        url = "/project_request_list/organisation/"
        response = self.admin_client.get(url)
        assert response.status_code == 200
