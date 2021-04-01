import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import routers

from crams.models import EResearchBodyIDKey
from crams.utils.crams_utils import get_random_string
from crams_allocation.test_utils import UnitTestCase
from crams_collection.models import ProjectID

class ProjectIdExistViewTest(UnitTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.client = self.auth_client(user=self.admin_user)
        # setup a project_id for prj_prov
        self.system = mixer.blend(EResearchBodyIDKey,
                                  type='I',
                                  key=get_random_string(15),
                                  e_research_body=self.erb)
        self.prj_id = mixer.blend(ProjectID, 
                                  identifier=get_random_string(15),
                                  project=self.prj_prov,
                                  system=self.system)

    def test_project_id_exist_view(self):
        url = reverse("project-id-exists", args=[self.system.id, self.prj_id.identifier])
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data['exists'] == True
        
    def test_project_id_not_exist_view(self):
        url = reverse("project-id-exists", args=[self.system.id, "non_existent_id"])
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data['exists'] == False
        
        