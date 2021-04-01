import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from tests.member.common_setup import CommonSetUp


# Tests project leader/admin inviting a user to join project
class TestInviteRequest(CommonSetUp):
    def setUp(self):
        CommonSetUp.setUp(self)
        # existing user contact payload
        self.existing_user = {
            'project_id': self.project1.id,
            'contact_id': self.member_contact2.id, 
            'email': self.member_contact2.email
            }
        # new user contact payload
        self.new_user = {
            "title":"mr",
            "given_name":"test",
            "surname":"tester",
            "email":"test@test.com",
            "project_id":self.project1.id
            }
    
    def project_invite_user(self, user, post_payload):
        client = self.user_auth_client(user)
        response = client.post('/member/project_leader_invite', post_payload)
        assert(response.status_code == 200)
        # check user was invited to project
        response = client.get('/member/project_leader_members/' + str(self.project1.id))
        results = response.json()
        member = next(item for item in results if item["email"] == post_payload['email'])
        assert(member['status_code'] == "I")
    
    def test_project_leader_invite_new_user(self):
        self.project_invite_user(self.user, self.new_user)

    def test_project_leader_invite_existing_user(self):
        self.project_invite_user(self.user, self.existing_user)
    
    def test_admin_invite_new_user(self):
        self.project_invite_user(self.admin, self.new_user)

    def test_admin_invite_existing_user(self):
        self.project_invite_user(self.admin, self.existing_user)
