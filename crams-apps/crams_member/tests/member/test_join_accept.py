import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from tests.member.common_setup import CommonSetUp


# Tests project leader accepting a user join request to a project
class TestJoinAccept(CommonSetUp):
    def accept_join_request(self, user):
        # setup a user join request
        post_payload = {'project_id': self.project1.id}
        client = self.user_auth_client(self.member2)
        response = client.post('/member/project_member_join', post_payload)
        # accept the join request
        post_payload = {
            "project_id": self.project1,
            "email": self.member_contact2.email,
            "action": "accept"
        }
        client = self.user_auth_client(user)
        response = client.post('/member/project_leader_request', post_payload)
        # check 200 ok response
        assert(response.status_code == 200)
        
        # check user join request has been rejected
        response = client.get('/member/project_leader_members/' + str(self.project1.id))
        results = response.json()
        # check 200 ok response
        assert(response.status_code == 200)
        member = next(item for item in results if item["email"] == self.member2.email)
        # check member status is "M" - Project Member
        assert(member['status_code'] == "M")

    def test_admin_accept_join_request(self):
        self.accept_join_request(self.admin)

    def test_prj_leader_accept_join_request(self):
        self.accept_join_request(self.user)