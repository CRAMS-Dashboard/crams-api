from rest_framework.reverse import reverse
from crams_contact.test_utils import UnitTestCase

class UnitTestCase(UnitTestCase):
    def setUp(self):
        pass

    def test_authenticate(self):
        # set temp password to login
        user, contact = self.generate_user_and_contact()
        
        password = 'password'
        user.set_password(password)
        user.save()
        client = self.auth_client()
        url = reverse('api_token_auth')
        response = client.post(url, {'username': user.username, 'password': password})

        assert response.status_code == 200

    def test_get_user_roles(self):
        admin_user, admin_contact, admin_token = self.generate_erb_admin_user_and_token()

        assert True

        
