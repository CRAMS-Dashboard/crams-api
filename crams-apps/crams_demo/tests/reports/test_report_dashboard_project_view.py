from mixer.backend.django import mixer

from crams_allocation.test_utils import UnitTestCase


class ReportDashboardProjectViewTest(UnitTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.testuser_client = self.auth_client(user=self.test_user)
        self.app_client = self.auth_client(user=self.app_user)
        self.admin_client = self.auth_client(user=self.admin_user)
        self.faculty_client = self.auth_client(user=self.faculty_user)

    def test_report_dashboard_list(self):
        url = "/reports/dashboard_project_list/"
        response = self.app_client.get(url)
        assert response.status_code == 200
        # check provision project
        prov_prj = next((x for x in response.data if x['project']['id'] == self.prj_prov.id), None)
        assert prov_prj
        assert prov_prj['project']['title'] == self.prj_prov.title
        assert prov_prj['project']['crams_id'] == self.prj_prov.crams_id
    
    def test_report_dashboard_list_no_projects(self):
        url = "/reports/dashboard_project_list/"
        # test client should have no projects under their name
        response = self.testuser_client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 0

    def test_report_dashboard_list_admin(self):
        url = "/reports/dashboard_project_list/admin/"
        response = self.admin_client.get(url)
        assert response.status_code == 200
        prov_prj = next((x for x in response.data if x['project']['id'] == self.prj_prov.id), None)
        assert prov_prj
        assert prov_prj['project']['title'] == self.prj_prov.title
        assert prov_prj['project']['crams_id'] == self.prj_prov.crams_id

    def test_report_dashboard_list_department(self):
        url = "/reports/dashboard_project_list/department/"
        response = self.admin_client.get(url)
        assert response.status_code == 200

    def test_report_dashboard_list_faculty(self):
        url = "/reports/dashboard_project_list/faculty/?e_research_body={}".format(self.erb.name)
        response = self.faculty_client.get(url)
        assert response.status_code == 200
        prov_prj = next((x for x in response.data if x['project']['id'] == self.prj_prov.id), None)
        assert prov_prj
        assert prov_prj['project']['title'] == self.prj_prov.title
        assert prov_prj['project']['crams_id'] == self.prj_prov.crams_id

    def test_report_dashboard_list_org(self):
        url = "/reports/dashboard_project_list/organisation/"
        response = self.admin_client.get(url)
        assert response.status_code == 200