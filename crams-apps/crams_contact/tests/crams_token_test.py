import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import routers
import json
from crams_contact.test_utils import UnitTestCase
from crams.models import User
from crams_contact.models import Contact, Organisation
from django.test import Client


class CramsTokenTest(UnitTestCase):
    def setUp(self):
        # set up user for testing
        self.user = mixer.blend(User, username='crams_user1@test.com',
                                first_name='test1',
                                last_name='user1',
                                email='crams_user1@test.com',
                                is_active=1)
        # set user password (call set_password method to hash the password
        self.user.set_password('test1234!')
        self.user.save()
        self.organisation = mixer.blend(Organisation, name='test organisation', short_name='mon',
                                        notification_email='test@crams.org.edu')
        self.contact = mixer.blend(Contact, title='Mr', given_name=self.user.first_name, surname=self.user.last_name,
                                   email=self.user.email, organisation=self.organisation)
        self.user_data = json.dumps({"username": "crams_user1@test.com", "password": "test1234!"})

    def test_crams_token(self):
        client = self.non_auth_client()
        token_response = client.post(reverse('api_token_auth'), data=self.user_data, content_type='application/json')
        assert token_response.status_code == 200
        assert token_response.data['token'] != None

    def test_user_roles(self):
        user_roles_url = reverse('user_roles')
        self.client = self.auth_client(user=self.user)
        user_roles_resp = self.client.get(user_roles_url)
        assert user_roles_resp.status_code == 200
        user_roles_data = user_roles_resp.data
        print(user_roles_data)
        assert user_roles_data['user_roles'] != None
