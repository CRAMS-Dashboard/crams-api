from mixer.backend.django import mixer

from crams_allocation.test_utils import UnitTestCase


class ReportStorageProductUsageViewTest(UnitTestCase):
    def setUp(self):
        super().setUp()
        self.generate_allocation_test_data()
        self.app_client = self.auth_client(user=self.app_user)
        self.admin_client = self.auth_client(user=self.admin_user)
        self.faculty_client = self.auth_client(user=self.faculty_user)

    # Not working yet
    def _test_storage_product_usage_view_list(self):
        url = '/reports/project_storage_product_usage/'
        response = self.app_client.get(url)
        assert response.status_code == 200

    # Not working yet
    def _test_storage_product_usage_view_detail(self):
        url = '/reports/project_storage_product_usage/{}/'.format(
            self.prj_prov.id)
        response = self.app_client.get(url)
        assert response.status_code == 200

    # Not working yet
    def _test_storage_product_usage_history_view_list(self):
        url = '/reports/project_storage_product_usage_history/'
        response = self.app_client.get(url)
        assert response.status_code == 200