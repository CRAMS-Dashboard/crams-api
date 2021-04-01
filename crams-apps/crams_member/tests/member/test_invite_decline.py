import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from tests.member.common_setup import CommonSetUp


# Tests user declining an invite to join a project
class TestInviteDecline(CommonSetUp):

    def test_user_invite_decline(self):
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

        # decline invite request
        post_payload = {
            'project_id': self.project1.id,
            'action': 'reject'
        }
        response = client.post('/member/project_member_request', post_payload)
        # check 200 ok reponse
        assert(response.status_code == 200)

        # check user has declined invite
        client = self.user_auth_client(self.user)
        response = client.get('/member/project_leader_members/' + str(self.project1.id))
        results = response.json()
        # check 200 ok response
        assert(response.status_code == 200)
        member = next(item for item in results if item["email"] == self.member2.email)
        # check member status is "D" - Invitation declined
        assert(member['status_code'] == "D")
