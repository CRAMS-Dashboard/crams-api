import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
from django.test import Client

from crams.models import CramsToken
from crams.models import User
from crams.models import EResearchBody
from crams.models import EResearchBodySystem
from crams_contact.models import Contact
from crams_contact.models import ContactRole
from crams_contact.models import CramsERBUserRoles
# from crams_allocation.models import Request
from crams_collection.models import Project
from crams_collection.models import ProjectContact
from crams_member.models import ProjectMemberStatus
from crams_member.models import ProjectJoinInviteRequest


class CommonSetUp(TestCase):
    def setUp(self):
        # setup admin user
        erb = mixer.blend(EResearchBody, name='erb')
        erbs = mixer.blend(EResearchBodySystem, name='erbs', e_research_body=erb)
        self.admin = self.create_user('erb@admin.com')
        self.admin_contact = mixer.blend(Contact, email=self.admin.email) 
        mixer.blend(CramsERBUserRoles, contact=self.admin_contact, role_erb=erb, is_erb_admin=True)
        # setup test projects
        self.project1 = mixer.blend(Project, title='Test Project 1', description='test project 1')
        self.project2 = mixer.blend(Project, title='Test Project 2', description='test project 2')
        self.request1 = mixer.blend(Request, project=self.project1, e_research_system=erbs)
        self.request2 = mixer.blend(Request, project=self.project2, e_research_system=erbs)
        # setup primary test user account
        self.user = self.create_user('joe@smith.com')
        self.user_contact = mixer.blend(Contact, given_name='Joe', surname='Smith', email='joe@smith.com')
        app_role = ContactRole.objects.get(name='Applicant')
        member_role = mixer.blend(ContactRole, name='Team Member')
        project_leader = mixer.blend(ContactRole, name='Project Leader', e_research_body=erb, project_leader=True)
        mixer.blend(ProjectContact, contact=self.user_contact, project=self.project1, contact_role=app_role)
        self.pm_status = ProjectMemberStatus.objects.get(code='M')
        # add primary user to project
        mixer.blend(ProjectJoinInviteRequest, email=self.user_contact.email, project=self.project1,
            status=self.pm_status, created_by=self.user, contact=self.user_contact)
        # setup test members
        self.member1 = self.create_user('test1@user.com')
        self.member2 = self.create_user('test2@user.com')
        self.member_contact1 = mixer.blend(Contact, given_name='test1', surname='test1', email='test1@user.com')
        self.member_contact2 = mixer.blend(Contact, given_name='test2', surname='test2', email='test2@user.com')
        mixer.blend(ProjectJoinInviteRequest, email=self.member_contact1.email, project=self.project1,
            status=self.pm_status, created_by=self.user, contact=self.member_contact1)
        mixer.blend(ProjectJoinInviteRequest, email=self.member_contact2.email, project=self.project2,
            status=self.pm_status, created_by=self.user, contact=self.member_contact2)
        mixer.blend(ProjectContact, contact=self.member_contact1, project=self.project1, contact_role=member_role)
        mixer.blend(ProjectContact, contact=self.member_contact2, project=self.project2, contact_role=member_role)

    def user_auth_client(self, user):
        # authenticate user and init cramstoken
        client = Client()
        client.login(username=user.username, password='password')
        crams_token = mixer.blend(CramsToken, user=user)
        client.defaults['authorization'] = crams_token.key
        return client

    def create_user(self, email):
        user = mixer.blend(User, username=email, email=email)
        user.set_password('password')
        user.save()
        return user
