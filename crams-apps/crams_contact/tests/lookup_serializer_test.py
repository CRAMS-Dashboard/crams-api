# https://github.com/django-json-api/django-rest-framework-json-api/blob/master/example/tests/test_serializers.py

import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from crams_contact.models import Organisation, Faculty, Department
from crams_contact.serializers.lookup_serializers import OrganisationLookupSerializer, FacultyLookupSerializer, \
    DepartmentLookupSerializer


# from rest_framework.renderers import JSONRenderer


class TestOrganisationCreated(TestCase):

    @pytest.mark.django_db
    def test_create_contact(self):
        organisation = mixer.blend(Organisation, name='test organisation',
                                   short_name='mon',
                                   notification_email='test@crams.org.edu',
                                   ands_url='www.ands.org/mon')
        organisation_result = Organisation.objects.last()
        assert organisation_result.notification_email == 'test@crams.org.edu'
        assert organisation.ands_url == 'www.ands.org/mon'


class TestOrganisationtLookupSerializer(TestCase):
    def setUp(self):
        organisation = mixer.blend(Organisation, name='test organisation',
                                   short_name='mon',
                                   notification_email='test@crams.org.edu',
                                   ands_url='www.ands.org/mon')
        organisation_result = Organisation.objects.last()
        self.serializer = OrganisationLookupSerializer(instance=organisation_result)

    def test_contact_lookup(self):
        data = self.serializer.data
        print('---- json data: {}'.format(data))
        assert data.get('notification_email') == None
        assert data['short_name'] == 'mon'
        assert data['name'] == 'test organisation'
        assert data.get('ands_url') == None


class TestFacultyLookupSerializer(TestCase):
    def setUp(self):
        self.json_data = {
            'faculty_code': 'test-0001',
            'name': 'Faculty of Engineering',
            'organisation': 'test organisation'}

        organisation = mixer.blend(Organisation, name='test organisation',
                                   short_name='mon',
                                   notification_email='test@crams.org.edu',
                                   ands_url='www.ands.org/mon')
        faculty = mixer.blend(Faculty, faculty_code='f_1001',
                              name='Faculty of Engineering',
                              organisation=organisation)

        self.serializer = FacultyLookupSerializer(instance=faculty)

    def test_faculty_lookup(self):
        data = self.serializer.data
        print('---- faculty json data: {}'.format(data))
        assert data['name'] == 'Faculty of Engineering'
        assert data['organisation'] == 'test organisation'

    def test_create_faculty(self):
        f_sz = FacultyLookupSerializer(data=self.json_data)

        # print('f_sz: {}'.format(f_sz))
        assert f_sz.is_valid() == True
        assert f_sz.validated_data != None
        try:
            f_sz.save()
            read_only = False
        except Exception:
            read_only = True

        assert read_only


class TestDepartmentLookupSerializer(TestCase):
    def setUp(self):
        self.json_data = {
            'faculty_code': 'test-0001',
            'name': 'Faculty of Engineering',
            'organisation': 'test organisation'}

        organisation = mixer.blend(Organisation, name='test organisation',
                                   short_name='mon',
                                   notification_email='test@crams.org.edu',
                                   ands_url='www.ands.org/mon')
        faculty = mixer.blend(Faculty, faculty_code='f_1001',
                              name='Faculty of Engineering',
                              organisation=organisation)
        dept = mixer.blend(Department, department_code='d-test-001', name='test department', faculty=faculty)
        self.serializer = DepartmentLookupSerializer(instance=dept)

    def test_department_lookup(self):
        data = self.serializer.data
        # json = JSONRenderer().render(data)
        # print('---- json: {}'.format(json))
        # print('----- department json: {}'.format(data))
        assert data['name'] == 'test department'
