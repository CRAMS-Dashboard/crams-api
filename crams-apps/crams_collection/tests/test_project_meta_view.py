import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import routers

from crams_allocation.test_utils import UnitTestCase


class ProjectMetaViewTest(UnitTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.app_client = self.auth_client(user=self.app_user)
        self.admin_client = self.auth_client(user=self.admin_user)
    
    def test_project_meta_list(self):
        url = "/project_metadata/"
        response = self.app_client.get(url)
        assert response.status_code == 200

        # check for submission project
        sub_prj = next((x for x in response.data if x['id'] == self.prj_submit.id), None)
        assert sub_prj['title'] == self.prj_submit.title
        assert sub_prj['description'] == self.prj_submit.description

        # check for approved project
        appr_prj = next((x for x in response.data if x['id'] == self.prj_approved.id), None)
        assert appr_prj['title'] == self.prj_approved.title
        assert appr_prj['description'] == self.prj_approved.description

        # check for provisioned project
        prov_prj = next((x for x in response.data if x['id'] == self.prj_prov.id), None)
        assert prov_prj['title'] == self.prj_prov.title
        assert prov_prj['description'] == self.prj_prov.description

    def test_project_meta_get(self):
        url = reverse('project-detail', args=[self.prj_submit.id])
        response = self.app_client.get(url)
        assert response.status_code == 200
        
        # check submit project returned
        sub_prj = response.data
        assert sub_prj['id'] == self.prj_submit.id
        assert sub_prj['title'] == self.prj_submit.title
        assert sub_prj['description'] == self.prj_submit.description
        
