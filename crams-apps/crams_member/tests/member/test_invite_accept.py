import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from tests.member.common_setup import CommonSetUp


# Tests admin/project leader accpeting an existing user invite
class TestInviteAccept(CommonSetUp):

    def invite_accept(self, user):
        # setup invite request
        post_payload = {
            'project_id': self.project1.id,
            'contact_id': self.member_contact2.id, 
            'email': self.member_contact2.email
        }
        client = self.user_auth_client(self.user)
        response = client.post('/member/project_leader_invite', post_payload)
        # check 200 ok reponse
        assert(response.status_code == 200)

        # accepting invite request
        post_payload = {
            "project_id": self.project1.id,
            "email": self.member_contact2.email,
            "action": "accept"
        }
        client = self.user_auth_client(user)
        response = client.post('/member/project_leader_request', post_payload)
        # check 200 ok response
        assert(response.status_code == 200)

        # check user is a member
        client = self.user_auth_client(self.user)
        response = client.get('/member/project_leader_members/' + str(self.project1.id))
        results = response.json()
        # check 200 ok response
        assert(response.status_code == 200)
        member = next(item for item in results if item["email"] == self.member2.email)
        # check member status is "M" - Project Member 
        assert(member['status_code'] == "M")

    def test_admin_invite_accept(self):
        self.invite_accept(self.admin)

    def test_prj_lead_invite_accept(self):
        self.invite_accept(self.user)