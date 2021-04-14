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
from crams.constants import db


class ProjectRequestViewUpdateExtensionTest(UnitTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.client = self.auth_client(user=self.app_user)

        # set the erbs to allow project meta change from
        # extending the allocation unless its a quota change
        from django.conf import settings
        settings.CRAMS_DEMO_ERB_SYSTEM = self.erbs.name
        from crams_racmon.config import config_init
        # config_init.EXTEND_ON_QUOTA_CHANGE.append(self.erbs.lower())
        

    def test_project_request_view_meta_update(self):
        # get payload
        url = "/project_request/{}/".format(self.prj_prov.id)
        response = self.client.get(url) 
        assert response.status_code == 200
        payload = response.data
        # meta update on project title and description
        payload['title'] = get_random_string(15)
        payload['description'] = get_random_string(200)

        response = self.client.put(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 200
        # check title and description change
        project = Project.objects.get(pk=response.data['id'])
        assert project.title == payload['title']
        assert project.description == payload['description']
        # check request status changed to application updated
        request = project.requests.all().first()
        assert request.request_status.code == db.REQUEST_STATUS_APPLICATION_UPDATED

    def test_project_request_view_quota_extension(self):
        # get payload
        url = "/project_request/{}/".format(self.prj_prov.id)
        response = self.client.get(url) 
        assert response.status_code == 200
        payload = response.data
        # update storage request quota extension 
        payload['requests'][0]['storage_requests'][0]['current_quota'] = 100
        payload['requests'][0]['storage_requests'][0]['requested_quota_change'] = 100
        payload['requests'][0]['storage_requests'][0]['requested_quota_total'] = 200
        payload['requests'][0]['storage_requests'][0]['approved_quota_change'] = 0
        payload['requests'][0]['storage_requests'][0]['approved_quota_total'] = 100

        response = self.client.put(url, data=json.dumps(payload), content_type="application/json")
        assert response.status_code == 200
        # check the request status
        request = Project.objects.get(pk=response.data['id']).requests.all().first()
        assert request.request_status.code == db.REQUEST_STATUS_UPDATE_OR_EXTEND
        # check the storage request quota updated
        storage_request = request.storage_requests.all().first()
        assert storage_request.current_quota == 100
        assert storage_request.requested_quota_change == 100
        assert storage_request.requested_quota_total == 200
        assert storage_request.approved_quota_change == 0
        assert storage_request.approved_quota_total == 100

        
