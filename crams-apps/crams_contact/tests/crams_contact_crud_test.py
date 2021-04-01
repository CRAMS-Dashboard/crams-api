# coding=utf-8
"""

"""
import pytest
from crams_contact.models import Organisation
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from crams.utils import crams_utils
from crams.models import User, EResearchBody
from crams_contact.models import Contact, CramsERBUserRoles
from crams_contact.serializers.contact_serializer import CramsContactSerializer
from crams_contact.serializers.contact_serializer import CramsContactDetailsLookupSerializer
from tests.role_free_contact_crud_test import ContactTestBase, RoleFreeContactDetailsLookupSerializer


class TestCramsContactDetailsLookupSerializer(ContactTestBase):
    def setUp(self):
        super().init_common(sz_class=RoleFreeContactDetailsLookupSerializer)
        self.normal_user = self.generate_new_user()
        self.erb_admin_user = self.generate_erb_admin_user()

    def common_create(self):
        another_user = self.generate_new_user()
        another_contact = self.create_test_contact_with_details(user=another_user, contact_id_list=['id01', 'id02'])
        context = {'current_user': self.normal_user}
        sz = CramsContactDetailsLookupSerializer(another_contact, context=context)
        return sz

    @pytest.mark.django_db
    def test_normal_user_should_not_see_other_contact_ids(self):
        another_user = self.generate_new_user()
        another_contact = self.create_test_contact_with_details(user=another_user, contact_id_list=['id01', 'id02'])
        context = {'current_user': self.normal_user}
        sz = CramsContactDetailsLookupSerializer(another_contact, context=context)
        print('----- normal user not see other contact ids - sz data: {}'.format(sz.data))
        assert 'contact_ids' not in sz.data

    @pytest.mark.django_db
    def test_normal_user_should_not_see_other_contact_details(self):
        another_user = self.generate_new_user()
        another_contact = self.create_test_contact_with_details(user=another_user, contact_id_list=['id01', 'id02'])
        context = {'current_user': self.normal_user}
        sz = CramsContactDetailsLookupSerializer(another_contact, context=context)
        print('===> normal user not see other contact_details - sz data: {}'.format(sz.data))
        contact_details = sz.data.get('contact_details')
        assert contact_details is None


class TestCramsContactSerializerSerializer(ContactTestBase):
    def setUp(self):
        super().init_common(sz_class=RoleFreeContactDetailsLookupSerializer)
        self.normal_user = self.generate_new_user()
        self.erb_admin_user = self.generate_erb_admin_user()

    @pytest.mark.django_db
    def test_admin_user_should_see_other_contact_ids(self):
        another_user = self.generate_new_user()
        another_contact = self.create_test_contact_with_details(user=another_user, contact_id_list=['id01', 'id02'])
        context = {'current_user': self.erb_admin_user}
        print('---- context: {}'.format(context))
        sz = CramsContactSerializer(another_contact, context=context)
        print('------ test_admin_user_should_see_other_contact_ids -> sz.data: {}'.format(sz.data))
        assert 'contact_ids' in sz.data
        contact_ids = sz.data.get('contact_ids')
        print('--- > contact ids: {}', contact_ids)
        # TODO, contact ids is not implemented
        # assert contact_ids is None
        assert contact_ids is not None

    @pytest.mark.django_db
    def test_admin_user_should_see_other_contact_details(self):
        another_user = self.generate_new_user()
        another_contact = self.create_test_contact_with_details(user=another_user, contact_id_list=['id01', 'id02'])
        context = {'current_user': self.erb_admin_user}
        sz = CramsContactSerializer(another_contact, context=context)
        print('------> test_admin_user_should_see_other_contact_details -> sz.data: {}'.format(sz.data))
        assert 'contact_details' in sz.data
        assert sz.data.get('contact_details') is not None


"""
from tests.crams_contact_crud_test import TestCramsContactDetailsLookupSerializer
self = TestCramsContactDetailsLookupSerializer()
self.setUp()

"""
