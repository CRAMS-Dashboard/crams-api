import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import routers

from crams_allocation.test_utils import UnitTestCase


class ContactProjectViewTest(UnitTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.app_client = self.auth_client(user=self.app_user)
        self.admin_client = self.auth_client(user=self.admin_user)

    def test_contact_project_list(self):
        url = "/contact/"
        response = self.app_client.get(url)
        assert response.status_code == 200
        # check applicant contact in the list
        app_contact = next((x for x in response.data if x['id'] == self.app_contact.id), None)
        assert app_contact['given_name'] == self.app_contact.given_name
        assert app_contact['surname'] == self.app_contact.surname
        assert app_contact['email'] == self.app_contact.email

    def test_contact_project_email(self):
        # get test applicant user contact details
        url = "/contact/{}/".format(self.app_contact.email)
        response = self.app_client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['given_name'] == self.app_contact.given_name
        assert response.data[0]['surname'] == self.app_contact.surname
        assert response.data[0]['email'] == self.app_contact.email
        # applicant should have multiple test projects setup
        assert len(response.data[0]['projects']) > 0

    def test_contact_project_contact_id(self):
        # get test project member user contact details
        url = "/contact/{}/".format(self.app_contact.id)
        response = self.app_client.get(url)
        assert response.status_code == 200
        assert response.data['given_name'] == self.app_contact.given_name
        assert response.data['surname'] == self.app_contact.surname
        assert response.data['email'] == self.app_contact.email

    def test_admin_contact_project_list(self):
        url = '/admin/contact/'
        response = self.admin_client.get(url)
        assert response.status_code == 200

        # check applicant contact in the list
        app_contact = next((x for x in response.data if x['id'] == self.app_contact.id), None)
        assert app_contact['given_name'] == self.app_contact.given_name
        assert app_contact['surname'] == self.app_contact.surname
        assert app_contact['email'] == self.app_contact.email

        # check prjmbr1_contact in the list
        prjmbr1_contact = next((x for x in response.data if x['id'] == self.prjmbr1_contact.id), None)
        assert prjmbr1_contact['given_name'] == self.prjmbr1_contact.given_name
        assert prjmbr1_contact['surname'] == self.prjmbr1_contact.surname
        assert prjmbr1_contact['email'] == self.prjmbr1_contact.email

        # check prjmbr2_contact in the list
        prjmbr2_contact = next((x for x in response.data if x['id'] == self.prjmbr2_contact.id), None)
        assert prjmbr2_contact['given_name'] == self.prjmbr2_contact.given_name
        assert prjmbr2_contact['surname'] == self.prjmbr2_contact.surname
        assert prjmbr2_contact['email'] == self.prjmbr2_contact.email

        # check prjmbr3_contact in the list
        prjmbr3_contact = next((x for x in response.data if x['id'] == self.prjmbr3_contact.id), None)
        assert prjmbr3_contact['given_name'] == self.prjmbr3_contact.given_name
        assert prjmbr3_contact['surname'] == self.prjmbr3_contact.surname
        assert prjmbr3_contact['email'] == self.prjmbr3_contact.email
        
    def test_admin_contact_project_contact_id_project(self):
        url = "/admin/contact/{}/".format(self.app_contact.id)
        response = self.admin_client.get(url)
        assert response.status_code == 200
        assert response.data['given_name'] == self.app_contact.given_name
        assert response.data['surname'] == self.app_contact.surname
        assert response.data['email'] == self.app_contact.email

    def test_admin_contact_project_email(self):
        # get test applicant user contact details
        url = "/admin/contact/{}/".format(self.app_contact.email)
        response = self.admin_client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['given_name'] == self.app_contact.given_name
        assert response.data[0]['surname'] == self.app_contact.surname
        assert response.data[0]['email'] == self.app_contact.email
        # applicant should have multiple test projects setup
        assert len(response.data[0]['projects']) > 0

    