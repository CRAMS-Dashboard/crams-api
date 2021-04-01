import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from crams_contact.models import ContactRole
from crams.models import EResearchBody
from crams_contact.serializers.contact_role import ContactRoleSerializer
from rest_framework import exceptions as rest_exceptions


class TestContactRoleModel(TestCase):
    @pytest.mark.django_db
    def test_create_contact_role(self):
        e_research_body = mixer.blend(EResearchBody, name='racmon', email='racmon@crams.org.edu')
        test_role = 'Role 1'
        contact_role = mixer.blend(ContactRole, name=test_role, e_research_body=e_research_body, project_leader=False,
                                   read_only=False, support_notification=False)
        assert contact_role.name == test_role


class TestContactRoleSerializer(TestCase):
    def setUp(self):
        self.e_research_body = mixer.blend(EResearchBody, name='racmon', email='racmon@crams.org.edu')
        self.contact_role = mixer.blend(ContactRole, name='admin', project_leader=True,
                                        e_research_body=self.e_research_body)
        self.serializer = ContactRoleSerializer(instance=self.contact_role)

    def test_contact_role(self):
        data = self.serializer.data
        assert data['name'] == 'admin'

    def test_create_role_should_fail(self):
        contact_role_json = {'name': 'admin1'}
        sz = ContactRoleSerializer(data=contact_role_json)
        assert sz.is_valid()
        with pytest.raises(rest_exceptions.ParseError):
            contact_role = sz.save()

    def test_update_role_should_fail(self):
        contact_role_data = self.serializer.data
        contact_role_data['name'] = 'updated_admin'
        sz = ContactRoleSerializer(data=contact_role_data)
        assert sz.is_valid()
        assert sz.validated_data['name'] == 'updated_admin'
        with pytest.raises(rest_exceptions.ParseError):
            updated_contact_role = sz.update(instance=self.contact_role, validated_data=sz.validated_data)
