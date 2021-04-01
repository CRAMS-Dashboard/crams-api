from rest_framework import routers

from crams_contact.views.contact_role import ContactRoleViewSet
from crams_contact.test_utils import UnitTestCase


class TestContactRoleViewSet(UnitTestCase):
    def setUp(self):
        self.client = self.auth_client()

    def test_contact_role(self):
        contact_role_views = ContactRoleViewSet()
        router = routers.DefaultRouter()
        contact_role_views.basename = router.get_default_basename(ContactRoleViewSet)
        contact_role_views.request = None
        contact_role_url = contact_role_views.reverse_action('list', args=[])
        get_contact_role_response = self.client.get(contact_role_url)
        assert get_contact_role_response.status_code == 200
        response_data = get_contact_role_response.data
        assert len(response_data) == 7
        print('contact role [0]: {}'.format(response_data[0]))
        assert response_data[0]['name'] == 'Applicant'
