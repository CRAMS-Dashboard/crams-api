import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from crams_contact.models import Organisation, Faculty, Department
from crams_contact.serializers.organisation_serializers import OrganisationSerializer, FacultySerializer, \
    DepartmentSerializer, DepartmentParentSerializer, DepartmentListSerializer


class TestOranisationSerializer(TestCase):
    def setUp(self):
        self.organisation = mixer.blend(Organisation, name='test organisation',
                                        short_name='mon',
                                        notification_email='test@crams.org.edu',
                                        ands_url='https://www.ands.org/mon')
        organisation_obj = Organisation.objects.all().last()
        self.serializer = OrganisationSerializer(instance=organisation_obj)

    def test_create_organisation(self):
        org_json_data = {'id': 1, 'name': 'test organisation', 'short_name': 'mon',
                         'notification_email': 'test@crams.org.edu', 'ands_url': 'https://www.ands.org/mon'}
        sz = OrganisationSerializer(data=org_json_data)
        assert sz.is_valid()
        instance = sz.save()

        assert instance.short_name == 'mon'
        assert instance.notification_email == 'test@crams.org.edu'
        assert instance.ands_url == 'https://www.ands.org/mon'

    def test_update_organisation(self):
        organisation_json_data = self.serializer.data
        organisation_json_data['short_name'] = 'mon_updated'
        organisation_json_data['notification_email'] = 'admin_test@crams.org.edu'
        organisation_json_data['ands_url'] = 'https://www.ands.org/mon_updated'
        sz = OrganisationSerializer(instance=self.organisation, data=organisation_json_data)
        assert sz.is_valid()
        sz.save()
        org_updated_obj = Organisation.objects.all().first()
        assert org_updated_obj.id == 1
        assert org_updated_obj.short_name == 'mon_updated'
        assert org_updated_obj.notification_email == 'admin_test@crams.org.edu'
        assert org_updated_obj.ands_url == 'https://www.ands.org/mon_updated'

    def test_ands_url_error_organisation(self):
        org_json_data = {'id': 1, 'name': 'test organisation', 'short_name': 'mon',
                         'notification_email': 'test@crams.org.edu', 'ands_url': 'www.ands.org/mon'}
        sz = OrganisationSerializer(data=org_json_data)
        assert sz.is_valid() == False
        assert 'ands_url' in sz.errors

    def test_notification_email_required_error_organisation(self):
        org_json_data = {'id': 1, 'name': 'test organisation', 'short_name': 'mon',
                         'ands_url': 'www.ands.org/mon'}
        sz = OrganisationSerializer(data=org_json_data)
        assert sz.is_valid() == False
        assert 'notification_email' in sz.errors


class TestFacultySerializer(TestCase):
    def setUp(self):
        self.organisation = mixer.blend(Organisation, name='test organisation',
                                        short_name='mon',
                                        notification_email='test@crams.org.edu',
                                        ands_url='https://www.ands.org/mon')
        faculty = mixer.blend(Faculty, faculty_code='50000565', name='Faculty of Engineering',
                              organisation=self.organisation)
        self.serializer = FacultySerializer(instance=faculty)

    def test_create_faculty(self):
        f_json_data = {'faculty_code': '50000568', 'name': 'Faculty of Arts',
                       'organisation': self.organisation.id}
        f_sz = FacultySerializer(data=f_json_data)
        assert f_sz.is_valid()
        instance = f_sz.save()
        assert instance.faculty_code == '50000568'
