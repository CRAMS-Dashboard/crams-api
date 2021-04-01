from crams.models import EResearchBody
from crams.test_utils import CommonBaseTestCase
from crams.utils import crams_utils
from django.contrib.auth import get_user_model
from mixer.backend.django import mixer

from crams_contact.models import Contact
from crams_contact.models import CramsERBUserRoles
from crams_contact.models import ContactRole
from crams_contact.serializers.contact_erb_roles import ContactErbRoleSerializer
User = get_user_model()


class UnitTestCase(CommonBaseTestCase):

    def generate_user_and_contact(self, user=None, org=None):
        if user is None:
            user = self.generate_new_user()
        contact = mixer.blend(Contact, 
                              given_name=user.username,
                              surname=user.username,
                              email=user.email,
                              organisation=org)

        return user, contact
    
    def generate_erb_admin_user_and_token(self, erb=None, user=None, org=None):
        # if user is None:
        #     user = self.generate_new_user()
        # contact = mixer.blend(Contact, email=user.email)
        user, contact = self.generate_user_and_contact(user=user, org=org)

        erb_prefix = crams_utils.get_random_string(8)
        if not erb:
            erb = mixer.blend(EResearchBody, name=erb_prefix + '_erb', email=erb_prefix + '@crams.org')
        mixer.blend(CramsERBUserRoles, role_erb=erb, is_erb_admin=True, contact=contact)
        crams_token = ContactErbRoleSerializer.setup_crams_token_and_roles(user_obj=user)
        return user, contact, crams_token

    def generate_contact_role(self, name, erb=None, project_leader=False, read_only=False, support_notification=False):
        return mixer.blend(ContactRole, 
                           name=name, 
                           e_research_body=erb, 
                           project_leader=project_leader,
                           read_only=read_only,
                           support_notification=support_notification)
    