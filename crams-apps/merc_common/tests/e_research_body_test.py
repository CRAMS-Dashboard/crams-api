from rest_framework.reverse import reverse

from crams.test_utils import CommonBaseTestCase


class TestContactRoleViewSet(CommonBaseTestCase):
    def setUp(self):
        self.client = self.auth_client()

    def test_e_research_body(self):
        # api action name: viewset basename + method name
        e_research_body_url = reverse('e_r_b-fetch-e-research-body')
        assert e_research_body_url != None
        e_research_body_response = self.client.get(e_research_body_url)
        assert e_research_body_response.status_code == 200
        json_data = e_research_body_response.data
        print(json_data)
        assert len(json_data) == 1
        assert json_data[0] == 'CRAMS-ERB'

    def test_e_research_system_by_e_r_body_name(self):
        e_r_system_url = reverse('e_r_b-fetch-e-research-systems', kwargs={"e_research_body": 'CRAMS-ERB'})
        assert e_r_system_url != None
        e_research_system_response = self.client.get(e_r_system_url)
        assert e_research_system_response.status_code == 200
        json_data = e_research_system_response.data
        assert len(json_data) > 0
        assert json_data[0]['name'] == 'CRAMS-ERB-SYS'
