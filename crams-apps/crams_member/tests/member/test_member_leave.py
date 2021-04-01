import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from tests.member.common_setup import CommonSetUp


# Tests project member request to leave a project
class TestmemberLeave(CommonSetUp):
    def test_member_leave(self):
        # user removing themself from a project
        post_payload = {'project_id': self.project1.id}
        client = self.user_auth_client(self.member1)
        response = client.post('/member/project_member_leave', post_payload)
        # check 200 ok response
        assert(response.status_code == 200)

        # check user no longer a member of project
        client = self.user_auth_client(self.user)
        response = client.get('/member/project_leader_members/' + str(self.project1.id))
        results = response.json()
        # check 200 ok response
        assert(response.status_code == 200)
        member = next(item for item in results if item["email"] == self.member2.email)
        # check member status is "V" - Membership revoked
        assert(member['status_code'] == "V")
