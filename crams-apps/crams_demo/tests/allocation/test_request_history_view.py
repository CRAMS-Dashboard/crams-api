import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import routers

from crams.constants import db
from crams_allocation.test_utils import UnitTestCase
from crams_collection.models import Project
from crams.models import EResearchBody, EResearchBodySystem
from crams_allocation.models import Request, RequestStatus
from crams_allocation.views.request_history import RequestHistoryViewSet
from django.utils.http import urlencode


class RequestHistoryViewTest(UnitTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.client = self.auth_client(user=self.app_user)

    def test_request_history(self):
        # test with a provisioned project
        req = self.prj_prov.requests.all().first()
        url = reverse("history-list") + '?' + urlencode({'request_id': req.id})
        response = self.client.get(url)
        print(response.data)
        assert response.status_code == 200
        # check there 3 history records submit, approved and provisioned
        assert len(response.data) == 3
        assert db.REQUEST_STATUS_SUBMITTED in (d['request_status']['code'] for d in response.data)
        assert db.REQUEST_STATUS_APPROVED in (d['request_status']['code'] for d in response.data)
        assert db.REQUEST_STATUS_PROVISIONED in (d['request_status']['code'] for d in response.data)
