from rest_framework.reverse import reverse
from crams.test_utils import CommonBaseTestCase


class TestFundingScheme(CommonBaseTestCase):
    def setUp(self):
        self.client = self.non_auth_client()

    def test_funding_scheme_by_erb_body(self):
        funding_scheme_api_url = reverse("funding_scheme", kwargs={"fb_name": "crams"})
        response = self.client.get(funding_scheme_api_url)
        assert response.status_code == 200
        json_data = response.data
        assert len(json_data) == 1
        assert response.json() is not None
