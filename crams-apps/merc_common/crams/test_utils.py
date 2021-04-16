from django.contrib.auth import get_user_model
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.test import APIClient

from crams_contact.serializers.contact_erb_roles import ContactErbRoleSerializer
from crams.models import CramsToken
from crams.utils import crams_utils

User = get_user_model()


class CommonBaseTestCase(TestCase):

    def non_auth_client(self):
        return APIClient()

    def auth_client(self, user=None, token=None):
        # authenticate user and init cramstoken
        client = APIClient()
        if not user:
            user = self.generate_new_user()
        # force user to login
        client.force_authenticate(user=user)
        if not token:
            token = ContactErbRoleSerializer.setup_crams_token_and_roles(user)

        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return client

    def generate_new_user(self):
        random_str = crams_utils.get_random_string(8)
        username = random_str
        email = username + '@crams.org'
        password = crams_utils.get_random_num_str(10)
        return mixer.blend(User, username=username, password=password, email=email)
