import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from tests.member.common_setup import CommonSetUp

# Tests user requesting to join a project
class TestJoinRequest(CommonSetUp):
    def test_join_project(self):
        post_payload = {'project_id': self.project2.id}
        client = self.user_auth_client(self.user)
        response = client.post('/member/project_member_join', post_payload)
        # check 200 ok response
        assert(response.status_code == 200)
        
        # get project join status
        client = self.user_auth_client(self.admin)
        response = client.get('/member/project_leader_members/' + str(self.project2.id))
        results = response.json()
        # check 200 ok response
        assert(response.status_code == 200)
        member = next(item for item in results if item["email"] == self.user.email)
        # check member status is "R" - Membership Request 
        assert(member['status_code'] == "R")

