from rest_framework.reverse import reverse
from crams.test_utils import CommonBaseTestCase


class TestGrantTypes(CommonBaseTestCase):
    def setUp(self):
        self.client = self.non_auth_client()

    def test_grant_types(self):
        grant_types_api_url = reverse("grant_types")
        response = self.client.get(grant_types_api_url)
        assert response.status_code == 200
        json_data = response.data
        assert len(json_data) == 7
        assert response.json() is not None
