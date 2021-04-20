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
from crams_allocation.product_allocation.models import StorageRequest
from crams_provision.test_utils import UnitTestCase as ProvTestCase


class ProvisionProjectViewExtensionTest(UnitTestCase, ProvTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.client = self.auth_client(user=self.provisioner_user)

    def test_provision_project_view_update_extension(self):
        # test provision project that have had its resource extended in detail display
        url = '/provision/storage_requests/update_provision_id_bulk/'
        
        # get the payload from updated/extensioned project
        payload = list()
        sp_req_list = self.prj_alloc_ext_appr.requests.all().first().storage_requests.all()
        for sp_req in sp_req_list:
            payload.append(self.get_storage_request_provision(sp_req, provision_id=sp_req.provision_id.provision_id))
        
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 200
        
        # check new request status is 'P' Provisioned
        storage_request = StorageRequest.objects.get(pk=response.data[0]['sp_provision']['id'])
        assert storage_request.request.request_status.code == 'P'
        for sp_req in sp_req_list:
            sp_prov = next((x for x in response.data if x['sp_provision']['id'] == sp_req.id), None)
            assert sp_prov
            assert sp_prov['success'] == True
            assert sp_prov['errors'] == None
            assert sp_prov['sp_provision']['provision_id'] != None
            assert sp_prov['sp_provision']['storage_product']['id'] == sp_req.storage_product.id

    def test_provision_project_view_update_extension_error(self):
        # test provisioning with an existing provision id
        # get existing provisioning id
        storage_request = self.prj_prov.requests.all().first().storage_requests.all().first()
        provision_id = storage_request.provision_id.provision_id
        payload = list()
        sp_req_list = self.prj_alloc_ext_appr.requests.all().first().storage_requests.all()
        for sp_req in sp_req_list:
            payload.append(self.get_storage_request_provision(
                sp_req, provision_id=provision_id))
        url = '/provision/storage_requests/update_provision_id_bulk/'
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 200
        # check for errors
        assert response.data[0]['success'] == False
        assert response.data[0]['errors'] != None