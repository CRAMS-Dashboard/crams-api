import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from tests.member.common_setup import CommonSetUp


# Tests admin/project leader accpeting an existing user invite and join request 
class TestMemberRevoke(CommonSetUp):
    def member_revoke(self, user):
        # revoke membership on user
        post_payload = {
            "project_id": self.project1.id,
            "email": self.member_contact1.email,
            "action": "reject"
        }
        client = self.user_auth_client(user)
        response = client.post('/member/project_leader_request', post_payload)
        # check 200 ok response
        assert(response.status_code == 200)

        # check user no longer a member of project
        response = client.get('/member/project_leader_members/' + str(self.project1.id))
        results = response.json()
        # check 200 ok response
        assert(response.status_code == 200)
        member = next(item for item in results if item["email"] == self.member2.email)
        # check member status is "V" - Membership revoked
        assert(member['status_code'] == "V")

    def test_admin_revoke_member(self):
        self.member_revoke(self.admin)

    def test_prj_leader_revoke_member(self):
        self.member_revoke(self.user)