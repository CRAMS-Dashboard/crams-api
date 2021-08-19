import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import routers
from django.utils.http import urlencode

from crams.utils.crams_utils import get_random_string
from crams_allocation.test_utils import UnitTestCase


class ProjectTitleExistsViewTest(UnitTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.client = self.auth_client(user=self.app_user)

    def test_existing_project_title(self):
        url = reverse("project-title-exists") + '?' + urlencode({'erb': self.erb.name, 'title': self.prj_prov.title})
        response = self.client.get(url)
        
        assert response.status_code == 200
        # project title exists 
        assert response.data == True
    
    def test_non_existing_project_title(self):
        url = reverse("project-title-exists") + '?' + urlencode({'erb': self.erb.name, 'title': get_random_string(50)})
        response = self.client.get(url)
        
        assert response.status_code == 200
        # project title does not exists 
        assert response.data == False