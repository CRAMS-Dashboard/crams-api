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
from crams_provision.test_utils import UnitTestCase as ProvTestCase

class ProvisionUpdateProvisionIDViewTest(UnitTestCase, ProvTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.client = self.auth_client(user=self.provisioner_user)

    def test_update_provision_id_view(self):
        sp_req = self.prj_prov.requests.all().first().storage_requests.all().first()
        url = '/provision/storage_requests/{}/update_provision_id/'.format(sp_req.id)
        # new provision id to update
        prov_id = get_random_string(20)
        # set up payload
        payload = self.get_provision_id_update_json(sp_req.storage_product, prov_id)
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 200
        
        # check provision id has been changed
        assert response.data['success'] == True
        assert response.data['errors'] == None
        assert response.data['sp_provision']['id'] == sp_req.id
        assert response.data['sp_provision']['provision_id'] == prov_id

    def test_update_provision_id_view_error(self):
        sp_req = self.prj_prov.requests.all().first().storage_requests.all().first()
        url = '/provision/storage_requests/{}/update_provision_id/'.format(sp_req.id)
        # get existing provision id to test update
        existing_sp = self.prj_alloc_ext.requests.all().first().storage_requests.all().first()
        payload = self.get_provision_id_update_json(sp_req.storage_product, 
                                                    existing_sp.provision_id.provision_id)
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 200

        # check for errors
        assert response.data['success'] == False
        assert response.data['errors'] != None