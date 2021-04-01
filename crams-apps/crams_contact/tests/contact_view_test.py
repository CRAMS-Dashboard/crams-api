import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import routers

from crams_contact.test_utils import UnitTestCase
from crams_contact.models import Contact
from crams_contact.views.contact import ContactViewSet
from crams_contact.models import Organisation


class ContactViewTest(UnitTestCase):
    def setUp(self):
        self.client = self.auth_client()
        # set up test contacts for searching
        self.contact1 = mixer.blend(Contact, 
                                    given_name='test1',
                                    surname='user1',
                                    email='contact1@test.com')
        self.contact2 = mixer.blend(Contact, 
                                    given_name='test1',
                                    surname='user2',
                                    email='contact2@test.com')
        self.contact3 = mixer.blend(Contact, 
                                    given_name='test1',
                                    surname='user3',
                                    email='contact3@test.com')
        self.contact_create = {'title': 'Mr',
                               'given_name': 'contact_create_given_name',
                               'surname': 'contact_create_surname',
                               'email': 'contact_create@test.com',
                               'phone': '99999999'}
        self.org = mixer.blend(Organisation, name='test organisation',
                          short_name='mon',
                          notification_email='test@crams.org.edu',
                          ands_url='https://www.ands.org/mon')

    def get_url(self, action, args=[], kwargs={}):
        contact_view = ContactViewSet()
        router = routers.DefaultRouter()
        contact_view.basename = router.get_default_basename(ContactViewSet)
        contact_view.request = None
        url = contact_view.reverse_action(action, args, kwargs)
        return url
    
    def test_search_contact(self):
        # test contact-list
        response = self.client.get(self.get_url('list'))
        assert response.status_code == 200

        # there could be some contacts already set up
        # this test will check only the ones created in the test setup()
        def find_contact(contact):
            for d in response.data:
                if d['email'] == contact.email:
                    if d['given_name'] == contact.given_name:
                        if d['surname'] == contact.surname:
                            return True
            return False
        if not find_contact(self.contact1):
            assert False
        if not find_contact(self.contact2):
            assert False
        if not find_contact(self.contact3):
            assert False

        # test contact-search-by-email
        response = self.client.get(self.get_url('search-by-email', args=[self.contact3.email]))
        assert response.status_code == 200
        assert response.data[0]['given_name'] == self.contact3.given_name
        assert response.data[0]['surname'] == self.contact3.surname
        assert response.data[0]['email'] == self.contact3.email

    def test_create_contact(self):
        contact_data = {
            "title": self.contact_create['title'],
            "given_name": self.contact_create['given_name'],
            "surname": self.contact_create['surname'],
            "email": self.contact_create['email'],
            "phone": self.contact_create['phone'],
            "organisation": {"id": self.org.id}
        }

        url = reverse("contact-list")
        response = self.client.post('/contact/', data=contact_data, format='json')
        print(response.data)
        print(url)
        print(contact_data)
        assert response.status_code == 201
        # check test contact is created
        test_contact = Contact.objects.get(pk=response.data['id'])
        assert test_contact.title == self.contact_create['title']
        assert test_contact.given_name == self.contact_create['given_name']
        assert test_contact.surname == self.contact_create['surname']
        assert test_contact.email == self.contact_create['email']
        assert test_contact.phone == self.contact_create['phone']
        assert test_contact.organisation == self.org
