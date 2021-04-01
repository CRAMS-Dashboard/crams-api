import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from tests.member.common_setup import CommonSetUp


# Tests admin/project leader declining an existing user invite and join request 
class TestDeclineOnUserBehalf(CommonSetUp):

    def decline_on_user_behalf(self, user):
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

        # decline the invite on user behalf
        post_payload = {
            "project_id": self.project1.id,
            "email": self.member_contact2.email,
            "action": "reject"
        }
        client = self.user_auth_client(user)
        response = client.post('/member/project_leader_request', post_payload)
        results = response.json()
        # check 200 ok response
        assert(response.status_code == 200)
        member = next(item for item in results if item["email"] == self.member2.email)
        # check member status is "D" - Invitation declined
        assert(member['status_code'] == "D")
    
    def test_admin_invite_decline_on_user_behalf(self):
        self.decline_on_user_behalf(self.admin)

    def test_prj_lead_invite_decline_on_user_behalf(self):
        self.decline_on_user_behalf(self.user)
