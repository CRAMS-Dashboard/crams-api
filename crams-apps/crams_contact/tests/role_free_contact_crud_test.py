# coding=utf-8
"""

"""
import pytest
from crams_contact.models import Organisation
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from crams.utils import crams_utils
from crams.models import User, EResearchBody, EResearchBodyIDKey
from crams_contact.models import CramsERBUserRoles
from crams_contact.serializers.contact_erb_roles import ContactErbRoleSerializer
from crams_contact.models import Contact, ContactDetail, EResearchContactIdentifier
from crams_contact.serializers.role_free_contact_serializer import RoleFreeContactSerializer
from crams_contact.serializers.role_free_contact_serializer import RoleFreeContactDetailsLookupSerializer


def get_new_contact_json(organisation_json=None):
    surname = crams_utils.get_random_string(8)
    email = "john." + surname + "@crams.org.edu"
    rnum = crams_utils.get_random_num_str(4)
    if not organisation_json:
        organisation_json = {
            "id": 1
        }
    c_json = {
        "title": "Mr",
        "given_name": "John",
        "surname": surname,
        "email": email,
        "phone": "4500" + rnum,
        "organisation": organisation_json,
        "orcid": "https://orcid.org/0000-4503-0003-" + rnum,
        "contact_details": [
            {
                "type": "Business",
                "email": email
            }
        ]
    }
    return c_json


class TestContactModel(TestCase):
    @pytest.mark.django_db
    def test_create_contact(self):
        organisation = mixer.blend(Organisation, name='test organisation', short_name='mon',
                                   notification_email='test@crams.org.edu')
        random_email = crams_utils.get_random_string(8) + '@crams.org.edu'
        contact = mixer.blend(Contact, title='Mr', given_name='John', surname='Doe',
                              email=random_email, organisation=organisation)
        assert contact.pk
        contact_result = Contact.objects.last()
        assert contact_result.email == random_email


class ContactTestBase(TestCase):
    def init_common(self, sz_class):
        organisation = mixer.blend(Organisation, name='test organisation', short_name='mon',
                                   notification_email='test@crams.org.edu')
        surname = crams_utils.get_random_string(8)
        random_email = surname + '@crams.org.edu'
        contact = mixer.blend(Contact, title='Mr', given_name='John', surname=surname,
                              email=random_email, organisation=organisation)
        contact_result = Contact.objects.last()
        assert contact_result is not None
        sz = sz_class(contact_result)
        assert isinstance(sz.data, dict)
        assert sz.data.get('email') == random_email
        assert sz.instance.pk
        self.serializer = sz

    @classmethod
    def generate_new_user(cls):
        random_str = crams_utils.get_random_string(8)
        username = random_str
        email = username + '@crams.org'
        return mixer.blend(User, username=username, email=email)

    @classmethod
    def generate_erb_admin_user(cls, erb_body=None, user=None):
        if not user:
            user = cls.generate_new_user()
        contact = mixer.blend(Contact, email=user.email)
        erb_prefix = crams_utils.get_random_string(8)
        if not erb_body:
            erb_body = mixer.blend(EResearchBody, name= erb_prefix + '_erb', email=erb_prefix + '@crams.org')
        mixer.blend(CramsERBUserRoles, role_erb=erb_body, is_erb_admin=True, contact=contact)
        ContactErbRoleSerializer.setup_crams_token_and_roles(user_obj=user)
        return user

    @classmethod
    def create_test_contact_with_details(cls, user=None, contact_id_list=None):
        def build_contact_details(type):
            phone = crams_utils.get_random_num_str(8)
            email = phone + '@crams.org'
            return mixer.blend(ContactDetail, parent_contact=contact, type=type, email=email, phone=phone)

        if not user:
            user = cls.generate_new_user()
        contact = mixer.blend(Contact, email=user.email)

        # set some contact details
        build_contact_details(type=ContactDetail.BUSINESS)
        build_contact_details(type=ContactDetail.MOBILE)

        if contact_id_list:
            key = crams_utils.get_random_string(4)
            erb = mixer.blend(EResearchBody, name=crams_utils.get_random_string(7))
            id_key = mixer.blend(EResearchBodyIDKey, type=EResearchBodyIDKey.ID_KEY, key=key, e_research_body=erb)
            for identifier in contact_id_list:
                cid = mixer.blend(EResearchContactIdentifier, identifier=identifier, contact=contact, system=id_key)
        contact = Contact.objects.get(pk=contact.pk)
        return contact


class TestRoleFreeContactDetailsLookupSerializer(ContactTestBase):
    def setUp(self):
        super().init_common(sz_class=RoleFreeContactDetailsLookupSerializer)

    def test_fetch_contacts(self):
        search_email = self.serializer.data.get('email')
        search_dict = {
            'email': search_email
        }
        qs = self.serializer.fetch_contacts(search_dict)
        assert qs.count() == 1
        assert qs.first().email == search_email

    def test_fetch_first_contact_obj(self):
        search_email = self.serializer.data.get('email')
        search_dict = {
            'email': search_email
        }
        obj = self.serializer.fetch_first_contact_obj(search_dict)
        assert isinstance(obj, Contact)
        assert obj.email == search_email

    def test_search_contact_get_queryset(self):
        def common_tst_script(qs):
            assert qs.count() == 1
            assert qs.first().email == search_email
            assert qs.first().pk == search_pk

        search_email = self.serializer.data.get('email')
        search_pk = self.serializer.instance.pk
        common_tst_script(self.serializer.search_contact_get_queryset(email=search_email))
        common_tst_script(self.serializer.search_contact_get_queryset(pk=search_pk))


class TestRoleFreeContactSerializer(ContactTestBase):
    def setUp(self):
        super().init_common(sz_class=RoleFreeContactSerializer)

    def test_contact_create(self):
        surname = crams_utils.get_random_string(8)
        email = "john." + surname + "@crams.org.edu"
        rnum = crams_utils.get_random_num_str(4)
        organisation_json = {
            "id": 1
        }
        c_json = {
            'title': 'Mr',
            'given_name': 'John',
            'surname': 'IO78WZLO',
            'email': email,
            'phone': '4500' + rnum,
            'organisation': organisation_json,
            'orcid': 'https://orcid.org/0000-4503-0003-6597',
            'contact_details': [
                {'type': 'Business', 'phone': None, 'email': 'john.io78wzlo@crams.org.edu'}],
        }
        sz = RoleFreeContactSerializer(data=c_json)
        sz.is_valid()
        assert sz.errors == dict()
        new_contact = sz.save()
        assert new_contact.pk

        obj_fetched = RoleFreeContactSerializer.fetch_first_contact_obj({'email': c_json.get('email')})
        assert obj_fetched == new_contact

        sz_created = RoleFreeContactSerializer(obj_fetched)
        for k, v in sz_created.data.items():
            if k == 'id':
                continue
            if k == 'organisation':
                assert v.get('id') == organisation_json.get('id')
                continue
            if k in ['latest_contact', 'scopusid'] :
                assert v is None
                continue
            if k == 'contact_ids':
                assert v == []
                continue
            if k == 'email':
                assert v == c_json.get(k).lower()
                continue
            assert v == c_json.get(k)

    # TODO: def test_contact_update(self):
    #     c_json = self.serializer.data
    #     new_name = 'New Name updated'
    #     c_json['given_name'] = new_name
    #     new_sz = CramsContactSerializer(data=c_json)
    #     new_sz.is_valid()
    #     print(new_sz.errors)
    #     assert new_sz.errors == {}
    #     updated = new_sz.save()
    #     assert updated.given_name == new_name

# class ContactCRUDTests(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         # Set up data for the whole TestCase
#         pass
#
#     @classmethod
#     def validate_contact_json(cls, contact_json, contact_obj, existing_contact=None):
#         def match_data(check_json, field_name, override_f_name_str=None):
#             field_val = check_json.get(field_name)
#             if field_val:
#                 attr_val = getattr(contact_obj, field_name)
#                 str_val = override_f_name_str or field_name
#                 msg = 'Contact {} does not match input json value'.format(str_val)
#                 cls.assertEqual(attr_val, field_val, msg)
#             elif existing_contact:
#                 msg = '{} was not in input json, yet changed'.format(field_name)
#                 cls.assertEqual(getattr(contact_obj, field_name), getattr(existing_contact, field_name), msg)
#
#         cls.assertIsNotNone(contact_obj, 'Contact instance cannot be None')
#         cls.assertIsNotNone(contact_obj.id, 'Contact not saved, pk is None')
#
#         match_data(contact_json, 'email')
#         match_data(contact_json, 'surname')
#         match_data(contact_json, 'given_name')
#         match_data(contact_json, 'title')
#         match_data(contact_json, 'phone')
#         match_data(contact_json, 'orcid')
#         match_data(contact_json, 'scopusid')
#
#         c_json_org = contact_json.get('organisation')
#         if c_json_org:
#             if 'id' in c_json_org:
#                 match_data(c_json_org, 'id', 'Organisation id')
#             elif 'name' in c_json_org:
#                 match_data(c_json_org, 'name', 'Organisation name')
#
#         # TODO Contact Details
#         # self.assertEqual(contact., c_json.get(''))
#
#     def createNewContactTest(self):
#         c_json = Contact1_Json
#         sz = ContactSerializer(data=c_json)
#         contact = sz.save()
#         self.validate_contact_json(c_json, contact)
#
#         # TODO validate serializer data fetch
#         return contact
#
#     def updateExistingContactTest(self):
#         existing_contact = self.createNewContactTest()
#         # TODO Change of email should fail
#         # TODO change of Title should succeed
#         # TODO change of Surname should succeed
#         # TODO change of Given Name should succeed
#         # TODO change of Phone should succeed
#         # TODO change of Orcid should succeed
#         # TODO change of Scopus id should succeed
#         # TODO change of contact details should succeed
#         #   - how to define changes to contact details
#         update_json = {
#             'email': existing_contact.email,
#             'title': existing_contact.title + '_extra'
#         }
#         sz = ContactSerializer(existing_contact, data=update_json)
#         sz.save()
