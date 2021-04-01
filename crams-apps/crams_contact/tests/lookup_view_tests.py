import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import routers

from crams_contact.test_utils import UnitTestCase
from crams_contact.models import Department
from crams_contact.models import Faculty
from crams_contact.models import Organisation
from crams_contact.views.organisation import DepartmentViewSet
from crams_contact.views.organisation import FacultyViewSet
from crams_contact.views.organisation import OrganisationViewSet


class TestLookupViewSet(UnitTestCase):
    def setUp(self):
        self.client = self.auth_client()
        # setup test org, faculty and dept data
        self.org = mixer.blend(Organisation, 
                               name='Organisation Test', 
                               short_name='org test', 
                               ands_url='https://ands-urls.org', 
                               notification_email='test@org.org')
        self.faculty = mixer.blend(Faculty,
                                   faculty_code='Fac0001',
                                   name='Faculty Test',
                                   organisation=self.org)
        self.department = mixer.blend(Department,
                                      department_code='Dept0001',
                                      name='Department Test',
                                      faculty=self.faculty)

    def get_url(self, action, viewset, args=[], kwargs={}):
        viewset = viewset()
        router = routers.DefaultRouter()
        viewset.basename = router.get_default_basename(viewset)
        viewset.request = None
        url = viewset.reverse_action(action, args, kwargs)
        return url

    def test_organisation_view(self):
        # test organisation-list
        response = self.client.get(self.get_url('list', OrganisationViewSet))
        assert response.status_code == 200
        # there could be some orgs already set up
        # this test will check only the ones created in the test setup()
        test_org_found = False
        for org in response.data:
            if org['name'] == self.org.name:
                if org['short_name'] == self.org.short_name:
                    if org['ands_url'] == self.org.ands_url: 
                        if org['notification_email'] == self.org.notification_email:
                            test_org_found = True
                            break
        if test_org_found:
            assert True
        else:
            assert False

        # test organisation-detail
        response = self.client.get(self.get_url('detail', OrganisationViewSet, args=[self.org.id]))
        assert response.status_code == 200
        assert response.data['name'] == self.org.name
        assert response.data['short_name'] == self.org.short_name
        assert response.data['ands_url'] == self.org.ands_url
        assert response.data['notification_email'] == self.org.notification_email

    def test_faculty_view(self):
        # test faculty-list
        response = self.client.get(self.get_url('list', FacultyViewSet))
        assert response.status_code == 200
        # there could be some faculty already set up
        # this test will check only the ones created in the test setup()
        test_fac_found = False
        for fac in response.data:
            if fac['name'] == self.faculty.name:
                if fac['faculty_code'] == self.faculty.faculty_code:
                    if fac['organisation'] == self.org.id:
                        test_fac_found = True
                        break
        if test_fac_found:
            assert True
        else:
            assert False
        
        # test faculty-detail
        response = self.client.get(self.get_url('detail', FacultyViewSet, args=[self.faculty.id]))
        assert response.status_code == 200
        assert response.data['name'] == self.faculty.name
        assert response.data['faculty_code'] == self.faculty.faculty_code
        assert response.data['organisation'] == self.org.id

        # test faculty-get-org-faculty
        response = self.client.get(self.get_url('get-org-faculty', FacultyViewSet, args=[self.org.id]))
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['name'] == self.faculty.name
        assert response.data[0]['faculty_code'] == self.faculty.faculty_code
        assert response.data[0]['organisation'] == self.org.id

    def test_department_view(self):
        # test departement-list
        response = self.client.get(self.get_url('list', DepartmentViewSet))
        assert response.status_code == 200
        # there could be some department already set up
        # this test will check only the ones created in the test setup()
        test_dept_found = False
        for dept in response.data:
            if dept['name'] == self.department.name:
                if dept['department_code'] == self.department.department_code:
                    if dept['faculty'] == self.faculty.id:
                        test_dept_found = True
                        break
        if test_dept_found:
            assert True
        else:
            assert False
        
        # test department-detail
        response = self.client.get(self.get_url('detail', DepartmentViewSet, args={self.department.id}))
        assert response.status_code == 200
        assert response.data['name'] == self.department.name
        assert response.data['department_code'] == self.department.department_code
        assert response.data['faculty'] == self.faculty.id
        
        # test department-get-faculty-department
        response = self.client.get(self.get_url('get-faculty-department', DepartmentViewSet, args={self.faculty.id}))
        assert response.status_code == 200
        assert response.data[0]['name'] == self.department.name
        assert response.data[0]['department_code'] == self.department.department_code
        assert response.data[0]['faculty'] == self.faculty.id
