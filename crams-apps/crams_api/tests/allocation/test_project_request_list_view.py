import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import routers

from crams_allocation.test_utils import UnitTestCase
from crams_manager.models import FacultyManager


class ProjectRequestListViewTest(UnitTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.app_client = self.auth_client(user=self.app_user)
        self.admin_client = self.auth_client(user=self.admin_user)
        # set up faculty manager account for app_user
        mixer.blend(FacultyManager, 
                    contact=self.admin_contact,
                    faculty=self.faculty,
                    active=True)

    def test_project_request_list(self):
        url = reverse("project-request-list-list")
        response = self.app_client.get(url)
        assert response.status_code == 200

        # check for submission project
        sub_prj = next((x for x in response.data['projects'] if x['id'] == self.prj_submit.id), None)
        assert sub_prj['title'] == self.prj_submit.title
        assert sub_prj['requests'][0]['request_status']['code'] == self.prj_submit.requests.all().first().request_status.code

        # check for approved project
        appr_prj = next((x for x in response.data['projects'] if x['id'] == self.prj_approved.id), None)
        assert appr_prj['title'] == self.prj_approved.title
        assert appr_prj['requests'][0]['request_status']['code'] == self.prj_approved.requests.all().first().request_status.code

        # check for provisioned project
        prov_prj = next((x for x in response.data['projects'] if x['id'] == self.prj_prov.id), None)
        assert prov_prj['title'] == self.prj_prov.title
        assert prov_prj['requests'][0]['request_status']['code'] == self.prj_prov.requests.all().first().request_status.code

    def test_project_request_admin_list(self):
        url = reverse("project-request-list-admin-list")
        response = self.admin_client.get(url)
        assert response.status_code == 200

        # check for submission project
        sub_prj = next((x for x in response.data['projects'] if x['id'] == self.prj_submit.id), None)
        assert sub_prj['title'] == self.prj_submit.title
        assert sub_prj['requests'][0]['request_status']['code'] == self.prj_submit.requests.all().first().request_status.code

        # check for approved project
        appr_prj = next((x for x in response.data['projects'] if x['id'] == self.prj_approved.id), None)
        assert appr_prj['title'] == self.prj_approved.title
        assert appr_prj['requests'][0]['request_status']['code'] == self.prj_approved.requests.all().first().request_status.code

        # check for provisioned project
        prov_prj = next((x for x in response.data['projects'] if x['id'] == self.prj_prov.id), None)
        assert prov_prj['title'] == self.prj_prov.title
        assert prov_prj['requests'][0]['request_status']['code'] == self.prj_prov.requests.all().first().request_status.code

    def test_project_request_dept_list(self):
        url = reverse("project-request-list-department-list")
        response = self.admin_client.get(url)
        assert response.status_code == 200

    # TODO: faculty not working
    def _test_project_request_faculty_list(self):
        url = reverse("project-request-list-faculty-list")
        response = self.admin_client.get(url)
        assert response.status_code == 200

    def test_project_request_org_list(self):
        url = reverse("project-request-list-organisation-list")
        response = self.admin_client.get(url)
        assert response.status_code == 200