import json
import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import routers

from crams.constants import db
from crams.utils.crams_utils import get_random_string
from crams_allocation.models import Request
from crams_allocation.test_utils import UnitTestCase


class DeclineRequestViewTest(UnitTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.client = self.auth_client(user=self.approver_user)

    def test_decline_request_view(self):
        req = self.prj_submit.requests.all().first()
        url = reverse('decline-request-detail', args=[req.id])
        url = '/decline_request/{}/'.format(req.id)
        # set up payload
        payload = {
            "approval_notes": get_random_string(50),
            "sent_email": False
        }
        response = self.client.put(url, data=json.dumps(payload), 
            content_type="application/json")
        assert response.status_code == 200

        decl_req = Request.objects.get(pk=response.data['id'])
        sub_req = Request.objects.filter(current_request=decl_req).first()
        # check submit request parent id matches new declined request id
        assert sub_req
        # check request has been declined
        assert decl_req.request_status.code == db.REQUEST_STATUS_DECLINED
        # check declined approval notes
        assert decl_req.approval_notes == payload['approval_notes']
