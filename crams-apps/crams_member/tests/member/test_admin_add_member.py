import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from tests.member.common_setup import CommonSetUp


# Tests admin adding a user directly to a project 
class TestAdminAddMember(CommonSetUp):
    def _test_adding_member(self, user):
        client = self.user_auth_client(user)
        post_payload = {
            'project_id': self.project1.id,
            'contact_id': self.member_contact2.id, 
            'contact_role': 'Team Member'
            }
        response = client.post('/member/project_admin_add_user', post_payload)
        # check 200 ok reponse
        assert(response.status_code == 200)
        # check contact 2 was added as a member to project 1
        response = client.get('/member/project_leader_members/' + str(self.project1.id))
        member = next(item for item in members if item["email"] == self.member_contact2.email)
        assert('Team Member' in member['roles'])
        assert(member['status_code'] == self.pm_status.code)

    # test admin adding a member to a project
    def test_admin_adding_member(self):
        self._test_adding_member(self.admin)

    # test project leader adding a member to a project
    def test_project_leader_adding_member(self):
        self._test_adding_member(self.user)

    # test non admin and non project leader adding a member to a project
    def test_unauth_user_adding_member(self):
        client = self.user_auth_client(self.user)
        post_payload = {
            'project_id': self.project2.id,
            'contact_id': self.member_contact1.id, 
            'contact_role': 'Team Member'
            }
        response = client.post('/member/project_admin_add_user', post_payload)
        # check 403 forbidden reponse
        assert(response.status_code == 403)
        