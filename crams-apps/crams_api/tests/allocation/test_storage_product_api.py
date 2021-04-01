from rest_framework.reverse import reverse

from crams.test_utils import CommonBaseTestCase


class TestStorageProductApi(CommonBaseTestCase):
    def setUp(self):
        self.client = self.auth_client()

    def test_storage_products_by_e_r_body_name(self):
        storage_product_api_url = reverse('storage_products', kwargs={"fb_name": 'NeCTAR'})
        assert storage_product_api_url != None
        storage_products_response = self.client.get(storage_product_api_url)
        assert storage_products_response.status_code == 200
        json_data = storage_products_response.data
        assert len(json_data) > 0
        assert json_data[0]['name'] == 'Volume (Intersect)'
