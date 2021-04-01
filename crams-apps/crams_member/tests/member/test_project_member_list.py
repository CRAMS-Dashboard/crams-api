import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from tests.member.common_setup import CommonSetUp


# Tests listing of members in a project and 
# project membership list of a user
class TestProjectMemberList(CommonSetUp):
    # Test user view of projects that user is a member of
    def test_user_project_list(self):
        client = self.user_auth_client(self.user)
        response = client.get('/member/project_member')
        results = response.json()
        # return 200 ok response
        assert(response.status_code == 200)
        # return 1 project test user is a member of
        assert(len(results) == 1)
        # check project, user email and status is correct
        assert(results[0]['project_id'] == self.project1.id)
        assert(results[0]['user_email'] == self.user_contact.email)
        assert(results[0]['status_code'] == self.pm_status.code)

    # Test project leader view of all members in a project
    def test_project_leader_member_list(self):
        client = self.user_auth_client(self.user)
        response = client.get('/member/project_leader_members/' + str(self.project1.id))
        results = response.json()
        # return 200 ok response
        assert(response.status_code == 200)
        # check correct project is returned
        assert(results['title'] == self.project1.title)
        # check only 2 members in the project
        members = results['members']
        assert(len(members) == 2)
        # check user is a member in the project
        member = next(item for item in members if item["email"] == self.user_contact.email)
        assert('Applicant' in member['roles'])
        assert(member['status_code'] == self.pm_status.code)
        # check test member 1 is a member in the project
        member = next(item for item in members if item["email"] == self.member_contact1.email)
        assert('Team Member' in member['roles'])
        assert(member['status_code'] == self.pm_status.code)

    
    # Test admin view of all members in a project
    def test_admin_member_list(self):
        client = self.user_auth_client(self.admin)
        response = client.get('/member/project_leader_members/' + str(self.project1.id))
        results = response.json()
        # return 200 ok response
        assert(response.status_code == 200)
        # check correct project is returned
        assert(results['title'] == self.project1.title)
        # check only 2 members in the project
        members = results['members']
        assert(len(members) == 2)
        # check user is a member in the project
        member = next(item for item in members if item["email"] == self.user_contact.email)
        assert('Applicant' in member['roles'])
        assert(member['status_code'] == self.pm_status.code)
        # check test member 1 is a member in the project
        member = next(item for item in members if item["email"] == self.member_contact1.email)
        assert('Team Member' in member['roles'])
        assert(member['status_code'] == self.pm_status.code)


    # Test user who is not a project leader can not see the project members view
    def test_unauth_access_to_member_list(self):
        client = self.user_auth_client(self.user)
        response = client.get('/member/project_leader_members/' + str(self.project2.id))
        # return 403 forbidden response
        assert(response.status_code == 403)

        
