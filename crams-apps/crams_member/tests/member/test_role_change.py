import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from tests.member.common_setup import CommonSetUp


# Tests changing a user membership role
class TestRoleChange(CommonSetUp):
    def change_role(self, user):
        # change test user role from "Team Member" to "Project Leader"
        post_payload = {
            'project_id': self.project1.id,
            'contact_id': self.member_contact1.id,
            'existing_role': 'Team Member',
            'new_role': 'Project Leader'
        }
        client = self.user_auth_client(user)
        response = client.post('/member/project_leader_set_role', post_payload)
        # check 200 ok reponse
        assert(response.status_code == 200)
        
        # check user role has changed to "Project Leader"
        response = client.get('/member/project_leader_members/' + str(self.project1.id))
        # check user role has been changed to Project Leader
        member = next(item for item in members if item["email"] == self.member_contact1.email)
        assert('Project Leader' in member['roles'])

    # Test admin change user role in a project
    def test_admin_change_role(self):
        self.change_role(self.admin)
    
    # Test project leader change user role in a project
    def test_prj_leader_change_role(self):
        self.change_role(self.user)
