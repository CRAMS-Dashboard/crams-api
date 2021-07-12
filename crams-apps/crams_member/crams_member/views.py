import logging
from json import dumps
from json import loads

from crams import permissions
from crams.constants import db
from crams.extension.config_init import DELEGATE_QUESTION_KEY_MAP
from crams.models import EResearchBody
from crams.models import EResearchBodyDelegate
from crams.models import Question
from crams.utils.django_utils import CramsModelViewSet
from crams_member.models import ProjectJoinInviteRequest
from crams.models import ProjectMemberStatus
from crams_collection.models import Project
from crams_collection.models import ProjectContact
from crams_collection.models import ProjectID
from crams_allocation.serializers.project_request_serializers import ProjectRequestSerializer
from crams_allocation.models import Request, RequestQuestionResponse
from crams_contact.models import Contact
from crams_contact.models import ContactRole
from crams_contact.models import CramsERBUserRoles
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import validate_email
from rest_framework import exceptions
from rest_framework import filters
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from crams_member.config.member_config import ERB_System_Membership_Email_fn_dict
from crams_member.config.member_config import get_email_processing_fn
from crams_member.serializers import ProjectIDSerializer
from crams_member.serializers import ProjectMemberInviteRequestSerializer
from crams_member.serializers import ProjectMemberSerialzer

# Email Recipient
# user who initiated request or invited by project leader or admin
INVITEE = 'Invited User'

# Hardcoded ContactRoles should be moved to common
ERB_ADMIN = 'E_RESEARCH_BODY Admin'
ERBS_ADMIN = 'E_RESEARCH_BODY_SYSTEM Admin'
ERBS_DELEGATE = 'E_RESEARCH_SYSTEM_DELEGATE'

# Actions
ACCEPT = 'accept'
REJECT = 'reject'

# logger to log errors
logger = logging.getLogger(__name__)


def get_project_request_serializer(project, data=None, context=None):
    if not data:
        return ProjectRequestSerializer(project, context=context)
    return ProjectRequestSerializer(project, data=data, context=context)


def is_valid_project_lead(user_contact, project):
    """
    Check user is a valid project leader who can invite/reject
    users to a project. If user is eresearch admin they have the
    same access as a project leader.
    :param user_contact:
    :param project:
    :return Boolean:
    """
    # get e_research_body from first request in project
    erbs = get_erbs(project)

    # check if contact is erb admin - supersedes project_leader
    if is_admin(user_contact, erbs):
        return True

    # check Project leader
    # get CI/project leader for e_research_body
    contact_roles = ContactRole.objects.filter(
        e_research_body=erbs.e_research_body,
        project_leader=True)

    # get project contacts to project
    p_contacts = ProjectContact.objects.filter(
        contact=user_contact, project=project,
        contact_role__in=contact_roles)

    if p_contacts.exists():
        return True

    # finally check if user is the applicant of the project
    app_contact_role = ContactRole.objects.get(name=db.APPLICANT)
    p_contact = ProjectContact.objects.filter(
        contact=user_contact, project=project,
        contact_role=app_contact_role)

    if p_contact.exists():
        return True

    # if missed all conditions return false
    return False


def is_admin(user_contact, erbs):
    # check if user is a erb admin
    erb_admin_contacts = CramsERBUserRoles.objects.filter(
        role_erb=erbs.e_research_body, contact=user_contact)

    # if user is an erb admin overrides the erbs admin
    for erb_admin_contact in erb_admin_contacts:
        if erb_admin_contact.is_erb_admin:
            return True

    # check if user is a erbs admin
    if erb_admin_contacts:
        if len(erb_admin_contacts) == 1:
            erb_admin_contact = erb_admin_contacts.first()
        else:
            # Fatal error users should have one or none CramsERBUserRole
            raise exceptions.ParseError(
                'User has more than one CramsERBUserRole')

        # if user is an erb admin overrides the erbs admin
        if erb_admin_contact.is_erb_admin:
            return True

        # check user erbs admin matches with current erbs
        for admin_erbs in erb_admin_contact.admin_erb_systems.all():
            if admin_erbs == erbs:
                return True

    return False


# gets the EResearchBodySystem from project object
def get_erbs(project):
    return project.requests.first().e_research_system


def reset_quota_change(project_obj, context, prj_sz=None):
    if prj_sz is None:
        prj_sz = get_project_request_serializer(project_obj, context=context)

    # convert to from ordered dict and modify quota
    prj_dict = loads(dumps(prj_sz.data, cls=DjangoJSONEncoder))

    for req in prj_dict['requests']:
        # set the request to no send an allocation updated/edit email when
        # adding/removing a contact to a project
        req['sent_email'] = False

        # The reason why we need to reset the approve quota is when updating 
        # the project/request the request serializer calls the function: 
        # "validate_approved_quota" (Ln:546) 
        # this will throws an exception when request is provisioned but has approved 
        # quota value in it. 
        
        # Important: 
        # Only set approve quota value to 0 when status is provisioned
        if req['request_status']['code'] == 'P':
            for s_req in req['storage_requests']:
                # set the approved_quota_change to 0 in storage requests
                # it will throw an exception if this value is not set to 0
                # resetting the quota to 0
                s_req['approved_quota_change'] = 0
                s_req['requested_quota_change'] = 0

    return get_project_request_serializer(
        project_obj, data=prj_dict, context=context)


# create/update project contact - triggers project update for archival
def create_update_project_contact(rest_request, project,
                                  contact, contact_role,
                                  prj_jn_inv_req):
    # Note: cannot use ProjectContactSerializer.add_given_user_as_project_contact method
    #       - because the project might require archival if moving from Provisioned status
    context = {'request': rest_request}
    prj_sz = get_project_request_serializer(project, context=context)

    # review existing project contacts to ensure no duplicates are added
    project_contacts = prj_sz.data.get('project_contacts', list())
    for project_contact in project_contacts:
        contact_id = project_contact.get('contact').get('id')
        if contact_id == contact.id:
            contact_role_id = project_contact.get('contact_role_id')
            if contact_role_id == contact_role.id:
                raise exceptions.ValidationError('Contact role exists {}/{}'.format(contact.email, contact_role.name))

    new_project_contact = {
        'contact': {
            'id': contact.id,
            'email': contact.email
        },
        'contact_role_id': contact_role.id,
        'contact_role': contact_role.name,
        'contact_role_erb': contact_role.e_research_body.name
    }

    prj_sz.data.get('project_contacts').append(new_project_contact)
    # reset the requested quota when saving the project
    update_project_sz = reset_quota_change(project, context, prj_sz=prj_sz)
    update_project_sz.is_valid(raise_exception=True)

    # save project serializer
    new_project = update_project_sz.save()

    # update project join invite request's project field if the project has changed
    if not new_project == project:
        prj_jn_inv_req.project_id = new_project.id
        prj_jn_inv_req.save()


# removing project contact - may trigger project archival, depends on erb rules in Project/Request serializer
def delete_project_contact(rest_request, project,
                           contact, prj_jn_inv_req):
    context = {'request': rest_request}
    prj_sz = get_project_request_serializer(project, context=context)
    project_contacts = prj_sz.data.get('project_contacts')
    if not project_contacts:
        raise exceptions.ValidationError('Project has no contacts')

    # removed the deleted contact from project contacts
    i = 0
    while i < len(prj_sz.data.get('project_contacts')):
        contact_id = prj_sz.data.get(
            'project_contacts')[i].get('contact').get('id')
        if contact_id == contact.id:
            del prj_sz.data.get('project_contacts')[i]
        i += 1

    # reset the requested quota when saving the project
    update_project_sz = reset_quota_change(
        project, context=context, prj_sz=prj_sz)
    update_project_sz.is_valid(raise_exception=True)

    # save project serializer
    new_project = update_project_sz.save()

    # update project join invite request's project field if the project has changed
    if not new_project == project:
        prj_jn_inv_req.project_id = new_project.id
        prj_jn_inv_req.save()


class ProjectJoinSearchViewSet(CramsModelViewSet):
    """
    class ProjectJoinSearchViewSet
        Public search of project using project title or
        project identifier
    """
    permission_classes = (permissions.IsCramsAuthenticated,)
    queryset = ProjectID.objects.none()
    serializer_class = ProjectIDSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('project__title', 'identifier')

    def fetch_e_research_body_param_obj(self, erb_name=None):
        if not erb_name:
            erb_name = self.request.query_params.get('e_research_body', None)
        if erb_name:
            try:
                return EResearchBody.objects.get(name__iexact=erb_name)
            except EResearchBody.DoesNotExist:
                msg = 'EResearchBody with name {} does not exist'
                raise exceptions.ValidationError(msg.format(erb_name))
        return None

    def get_queryset(self):
        # get provisioned projects
        project_set = set()
        req_qs = Request.objects.filter(
            request_status__code=db.REQUEST_STATUS_PROVISIONED)

        # filter by erb_obj
        erb_obj = self.fetch_e_research_body_param_obj()
        if erb_obj:
            req_qs = req_qs.filter(e_research_system__e_research_body=erb_obj)

        for req in req_qs.all():
            project = req.project
            if project.current_project:
                project = project.current_project
            project_set.add(project)

        return ProjectID.objects.filter(project__in=project_set,
                                        parent_erb_project_id=None)


class ProjectAdminAddUserViewSet(APIView):
    """
    class ProjectLeaderAddUserViewSet
        Project leader adding a user directly using an existing
        contact entry. User becomes a member instantly no confirmation
        or acceptance is required from user
    """
    permission_classes = (permissions.IsCramsAuthenticated,)

    project = ""
    contact = ""
    contact_role = ""
    admin_user = ""
    admin_user_contact = ""
    sent_email = True  # default value

    def get_request_data(self, request):
        try:
            project_id = request.data['project_id']
            contact_id = request.data['contact_id']
            contact_role = request.data['contact_role']
            sent_email = request.data.get('sent_email')

            self.project = Project.objects.get(pk=project_id)
            if self.project.current_project:
                self.project = self.project.current_project
            self.contact = Contact.objects.get(pk=contact_id)
            self.contact_role = ContactRole.objects.get(
                name__iexact=contact_role)
            if type(sent_email) is bool:
                self.sent_email = sent_email

            self.admin_user = request.user
            self.admin_user_contact = Contact.objects.get(
                email=self.admin_user.email)

            return True
        except:
            return False

    def add_user(self):
        # create/update entry in ProjectJoinInviteRequest
        prj_join_inv_req_list = ProjectJoinInviteRequest.objects.filter(
            project=self.project, email=self.contact.email)

        if prj_join_inv_req_list.exists():
            # updating existing ProjectJoinInviteRequest
            prj_join_inv_req = prj_join_inv_req_list.first()

            # reset the name from contact, might have been updated since
            prj_join_inv_req.given_name = self.contact.given_name
            prj_join_inv_req.surname = self.contact.surname

            # if user is already a member throw an error
            if prj_join_inv_req.status.code == 'M':
                raise exceptions.ParseError(
                    "User is already a member of the project.")

            prj_join_inv_req.updated_by = self.request.user
        else:
            # saving a new ProjectJoinInviteRequest
            prj_join_inv_req = ProjectJoinInviteRequest()
            # prj_join_inv_req.project = self.project
            prj_join_inv_req.email = self.contact.email
            prj_join_inv_req.surname = self.contact.surname
            prj_join_inv_req.given_name = self.contact.given_name
            prj_join_inv_req.created_by = self.request.user
            prj_join_inv_req.contact = self.contact
            prj_join_inv_req.project = self.project

        # set the status to "Project Member(M)"
        try:
            member_status = ProjectMemberStatus.objects.get(code="M")
            prj_join_inv_req.status = member_status
        except:
            raise exceptions.ParseError(
                "Unable to find ProjectMemberStatus code: 'M'")

        # save the membership first otherwise it will double up 
        # when project contact serializer doesn't find the membership 
        # it will try to create one on update
        prj_join_inv_req.save()

        # update project archival
        try:
            create_update_project_contact(rest_request=self.request,
                                          project=self.project,
                                          contact=self.contact,
                                          contact_role=self.contact_role,
                                          prj_jn_inv_req=prj_join_inv_req)
        except:
            # rollback by removing membership if project update fails
            prj_join_inv_req.delete()
            raise exceptions.ParseError(
                "Unable to update project contact")

        # return ProjectJoinInvitationRequest for email notification
        return prj_join_inv_req

    def post(self, request):
        if not self.get_request_data(request):
            raise exceptions.ParseError(
                "Incomplete fields or could not find project, contact or " +
                "project_contact.")

        # get e_research_body_system
        erbs = get_erbs(self.project)

        # check if user is valid project leader
        if not is_valid_project_lead(self.admin_user_contact, self.project):
            raise exceptions.PermissionDenied(
                "Access denied, user is not a project leader or admin")

        # add user to project
        prj_join_inv_req = self.add_user()

        # send notification
        if self.sent_email:
            email_processing_fn = get_email_processing_fn(ERB_System_Membership_Email_fn_dict, erbs)
            email_processing_fn(subject="Project membership to: ",
                                prj_join_invite_request=prj_join_inv_req,
                                member_status_code='M',
                                # using admin to populate the name in template
                                prj_lead_contacts=[self.admin_user_contact],
                                erbs=erbs)

        return Response({"detail": "User added"},
                        status=status.HTTP_200_OK)


class ProjectLeaderSetRoleViewSet(APIView):
    """
    class ProjectLeaderSetRole
        Project leader or admin set the role of existing user
    """
    permission_classes = (permissions.IsCramsAuthenticated,)

    prj_lead_user_contact = ""
    project = ""
    contact = ""
    existing_role = ""
    new_role = ""

    def get_request_data(self, request):
        # if successful extracting request data returns True
        try:
            self.prj_lead_user_contact = Contact.objects.get(
                email=request.user.email)

            self.project = Project.objects.get(pk=request.data['project_id'])
            if self.project.current_project:
                self.project = self.project.current_project
            self.contact = Contact.objects.get(pk=request.data['contact_id'])
            if request.data.get('existing_role'):
                self.existing_role = ContactRole.objects.get(
                    name__iexact=request.data["existing_role"])
            else:
                self.existing_role = None
            self.new_role = ContactRole.objects.get(
                name__iexact=request.data["new_role"])

            return True
        except:
            return False

    def set_role(self):
        # check user has role current role in project
        prj_contact = None
        try:
            prj_contact = ProjectContact.objects.get(
                project=self.project,
                contact=self.contact,
                contact_role=self.existing_role)
        except:
            # it is possible user is the applicant but not a project leader
            # this will check if user is an applicant(Can only be 1 applicant
            # per project), then create a new project leader role ProjectContact
            try:
                applicant_role = ContactRole.objects.get(name=db.APPLICANT)
                applicant_contact = ProjectContact.objects.get(
                    project=self.project,
                    contact=self.contact,
                    contact_role=applicant_role)
                # if user is applicant create a new project contact
                if applicant_contact:
                    prj_contact = ProjectContact()
                    prj_contact.project = self.project
                    prj_contact.contact = self.contact

            except:
                raise exceptions.ParseError(
                    "Either user current role, project or contact" +
                    "does not exist. ")

        if prj_contact:
            context = {'request': self.request}
            # get existing project data
            prj_serializer = get_project_request_serializer(self.project, context=context)

            # update project serializer for archival purposes
            new_prj_serializer = get_project_request_serializer(self.project,
                                                        data=prj_serializer.data,
                                                        context=context)
            new_prj_serializer.is_valid()
            new_prj_serializer.save()

            if self.existing_role:
                # get the new project contact
                new_pc = ProjectContact.objects.get(
                    project_id=new_prj_serializer.data['id'],
                    contact=prj_contact.contact,
                    contact_role=self.existing_role)
            else:
                new_pc = ProjectContact(project_id=new_prj_serializer.data['id'],
                                        contact=prj_contact.contact)

            new_pc.contact_role = self.new_role
            new_pc.save()

            # return the new project id
            return new_prj_serializer.data['id']

    def post(self, request):
        # get request data
        if not self.get_request_data(request):
            raise exceptions.ParseError(
                "Incomplete fields or could not " +
                "find project or contact information.")

        # check if user is a valid CI for project
        if not is_valid_project_lead(self.prj_lead_user_contact,
                                     self.project):
            raise exceptions.PermissionDenied(
                "Access denied, user is not a project leader or admin")

        # set the new role and get the new project id from archival
        new_project_id = self.set_role()

        # get project join invite request for email notification
        prj_jn_inv_req = ProjectJoinInviteRequest.objects.get(
            project_id=new_project_id, email=self.contact.email)

        if self.existing_role:
            old_role = self.existing_role.name
        else:
            old_role = None

        # reset the name from contact, might have been updated since
        prj_jn_inv_req.given_name = self.contact.given_name
        prj_jn_inv_req.surname = self.contact.surname
        prj_jn_inv_req.save()

        # get e_research_body_system from project
        erbs = get_erbs(self.project)

        # send notification
        email_processing_fn = get_email_processing_fn(ERB_System_Membership_Email_fn_dict, erbs)
        email_processing_fn(subject="User role changed in project: ",
                            prj_join_invite_request=prj_jn_inv_req,
                            member_status_code='U',
                            prj_lead_contacts=[self.prj_lead_user_contact],
                            additional_params={
                                "old_role": old_role,
                                "new_role": self.new_role.name},
                            erbs=erbs)
        return Response({"detail": "User role changed"},
                        status=status.HTTP_200_OK)


class ProjectLeaderInviteViewSet(APIView):
    """
    class ProjectLeaderInviteViewSet
        Project leader invites a user to join project
    """
    permission_classes = (permissions.IsCramsAuthenticated,)

    project = ""
    prj_lead_user = ""
    prj_lead_user_contact = ""
    erb = ""
    erbs = ""

    # contact details - default None
    contact = None
    contact_role = None

    # invitee details
    title = ''
    given_name = ''
    surname = ''
    email = ''

    def get_request_data(self, request):
        # try and get id's from request data
        try:
            # get user details
            if "contact_id" in request.data:
                # make sure other details are not present can double up
                other_details = ["title", "given_name", "surname", "email"]
                double_up_list = [
                    i for i in other_details if i in [*request.data]]
                if double_up_list:
                    raise exceptions.ParseError(
                        "You have provided the 'contact_id' and/or member "
                        "'given_name', 'surname' and 'email'. "
                        "Please provide either "
                        "the 'contact_id' or the full member details.")

                self.contact = \
                    Contact.objects.get(pk=request.data["contact_id"])
                self.given_name = self.contact.given_name
                self.surname = self.contact.surname
                self.email = self.contact.email
            else:
                self.email = request.data["email"]
                # check if user contact exist using email
                try:
                    self.contact = Contact.objects.get(email=self.email)
                    # reuse existing details in contact object
                    self.given_name = self.contact.given_name
                    self.surname = self.contact.surname
                except:
                    # if contact not found then save new details
                    # title is optional so may not be in request.data
                    if "title" in request.data:
                        self.title = request.data["title"]
                    self.given_name = request.data["given_name"]
                    self.surname = request.data["surname"]

            project_id = request.data["project_id"]

            # try and get required objects
            project = Project.objects.get(pk=project_id)

            # get the latest project if this is not the latest
            self.project = self.get_latest_project(project)
            self.prj_lead_user = request.user
            self.prj_lead_user_contact = Contact.objects.get(
                email=self.prj_lead_user.email)

            # get project's eResearchBody and eResearchSystem
            self.erb = self.project.requests.first() \
                .e_research_system.e_research_body

            self.erbs = self.project.requests.first() \
                .e_research_system

        except exceptions.ParseError as ex:
            raise ex
        except:
            raise exceptions.ParseError(
                "Incomplete fields or could not find project")

    def valid_name_and_email(self):
        # ensure the name and email is provided in request
        # if not self.given_name:
        #     return False
        #
        # if not self.surname:
        #     return False

        if self.email:
            try:
                # ensure email is valid
                validate_email(self.email)
            except:
                return False
        else:
            return False

        return True

    def get_latest_project(self, project):
        if project.current_project is not None:
            # if project is not the latest try and fetch return it
            return project.current_project
        else:
            return project

    def _is_valid_project_lead(self):
        try:
            # get CI/project leader for e_research_body
            contact_roles = ContactRole.objects.filter(
                e_research_body=self.erb, project_leader=True)

            p_contacts = ProjectContact.objects.filter(
                contact=self.prj_lead_user_contact, project=self.project,
                contact_role__in=contact_roles)

            if p_contacts.exists():
                return True
            else:
                return False
        except:
            return False

    def invite_user(self, prj_invite):
        # get invite project status
        prj_member_status = ProjectMemberStatus.objects.get(code='I')

        if not prj_invite:
            # create an entry for inviting user
            prj_invite = ProjectJoinInviteRequest()

            prj_invite.title = self.title
            prj_invite.given_name = self.given_name
            prj_invite.surname = self.surname
            prj_invite.email = self.email
            prj_invite.project = self.project
            prj_invite.status = prj_member_status
            prj_invite.created_by = self.prj_lead_user
        else:
            # update existing project join invite request
            prj_invite.status = prj_member_status
            prj_invite.updated_by = self.prj_lead_user

        prj_invite.save()

        return prj_invite

    def post(self, request, fail_siliently=True):
        # get request data
        self.get_request_data(request)

        # check if user is a valid CI for project
        if not is_valid_project_lead(self.prj_lead_user_contact,
                                     self.project):
            raise exceptions.PermissionDenied(
                "Access denied, user is not a project leader or admin")

        # check valid mandatory fields name and email
        if not self.valid_name_and_email():
            raise exceptions.ParseError(
                "Invalid given_name, surname or email")

        # check if user is current a member or has been invited already
        project_invites = ProjectJoinInviteRequest.objects.filter(
            project=self.project, email=self.email)

        prj_invite = None
        if project_invites.exists():
            prj_invite = project_invites.first()

            # reset the name from contact, might have been updated since
            prj_invite.given_name = self.contact.given_name
            prj_invite.surname = self.contact.surname
            prj_invite.save()

        # check membership status
        if prj_invite:
            # user already a member
            if project_invites.first().status.code == 'M':
                raise exceptions.ParseError(
                    "User is already a member of project")

            # user has already been invited
            if project_invites.first().status.code == 'I':
                raise exceptions.ParseError(
                    "User has already been invited to project")

            # user has already requested to join
            if project_invites.first().status.code == 'R':
                raise exceptions.ParseError(
                    "User has already requested to join project")

        # set user invite
        prj_invite = self.invite_user(prj_invite=prj_invite)

        # get the user who created or updated invite request,
        # that user should be the project leader who sent out the invited
        if prj_invite.updated_by:
            prj_lead_contact = Contact.objects.get(
                email=prj_invite.updated_by.email)
        else:
            prj_lead_contact = Contact.objects.get(
                email=prj_invite.created_by.email)
        
        # get e_research_body_system from project
        erbs = get_erbs(self.project)

        # send invitation to user
        email_processing_fn = get_email_processing_fn(ERB_System_Membership_Email_fn_dict, erbs)
        email_processing_fn(subject='Invite to project: ',
                            prj_join_invite_request=prj_invite,
                            member_status_code="I",
                            prj_lead_contacts=[prj_lead_contact],
                            erbs=erbs)

        return Response({"detail": "Invitation Sent"},
                        status=status.HTTP_200_OK)


class ProjectMemberViewSet(viewsets.GenericViewSet,
                           mixins.ListModelMixin):
    """
        class ProjectMemberViewSet
            Views all projects user is a member of, all projects user is
            invited to join and projects the user has requested to join
        """
    permission_classes = (permissions.IsCramsAuthenticated,)
    serializer_class = ProjectMemberInviteRequestSerializer
    queryset = ProjectJoinInviteRequest.objects.all()

    def get_queryset(self):
        queryset = self.queryset.filter(email=self.request.user.email)

        # check ProjectContact first
        contact = Contact.objects.get(email=self.request.user.email)
        prj_contacts = ProjectContact.objects.filter(
            contact=contact,
            project__current_project=None).values('project').distinct()

        # grab all the projects from ProjectContact that user is a
        # member of to check against
        member_prj_list = []
        for prj_jn_inv_req in queryset:
            member_prj_list.append(prj_jn_inv_req.project)

        # add entry into ProjectJoinInviteRequest if user has a
        # ProjectContact that doesn't match with a project
        for prj_contact in prj_contacts:
            # check project_contact - project has been provisioned
            project = Project.objects.get(pk=prj_contact['project'])
            # prj_prov_dets = ProjectProvisionDetails.objects.filter(
            #     project=project)

            # check provision status
            provisioned = False
            for req in project.requests.all():
                # Check for the following provisioned request
                # P - Request has been provisioned
                # X - Request provisioned and requested an extension
                # J - Request provisioned and requested extension declined
                valid_status_code = ['P', 'X', 'J']
                if req.request_status.code in valid_status_code:
                    provisioned = True
                    break

            if provisioned:
                # add project details to users ProjectJoinInviteRequest if
                # nothing has been recorded
                if not project in member_prj_list:
                    # create new prj_jn_inv_req entry and set as member
                    new_member = ProjectJoinInviteRequest()
                    new_member.surname = contact.surname
                    new_member.given_name = contact.given_name
                    new_member.email = contact.email
                    new_member.project = project
                    new_member.status = \
                        ProjectMemberStatus.objects.get(code='M')
                    new_member.created_by = self.request.user
                    new_member.contact = contact
                    new_member.save()
                else:
                    # if existing check membership status
                    membership = queryset.filter(project=project)

                    if len(membership) > 1:
                        # The should be only 1 prj_jn_inv_req entry for
                        # a user per project
                        raise exceptions.ParseError(
                            "Multiple request entries detected")

                    if len(membership) == 1:
                        # if user not a member update the status
                        if membership[0].status.code != 'M':
                            membership[0].status = \
                                ProjectMemberStatus.objects.get(code='M')
                            membership[0].save()

        # update the queryset if any missing projects from ProjectContact
        # were added above
        queryset = self.queryset.filter(email=self.request.user.email)

        return queryset


class ProjectLeaderMemberViewSet(viewsets.GenericViewSet,
                                 mixins.RetrieveModelMixin):
    """
    class ProjectLeaderMemberViewSet
        Views all project members in project
    """
    permission_classes = (permissions.IsCramsAuthenticated,)

    serializer_class = ProjectMemberSerialzer
    queryset = Project.objects.all()

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        try:
            project = self.get_queryset().get(pk=pk)
            # make sure project is the latest parent
            if project.current_project is not None:
                project = project.current_project
            user_contact = Contact.objects.get(email=request.user.email)

        except:
            raise exceptions.ParseError("Project not found")

        if not is_valid_project_lead(user_contact, project):
            raise exceptions.PermissionDenied(
                "Access denied, user is not a project leader or admin")

        return Response(ProjectMemberSerialzer(project).data)


class ProjectLeaderRequestViewSet(APIView):
    """
    class ProjectLeaderRequest
        Accepts, Decline, Reject and Revokes
        project member requests
    """
    permission_classes = (permissions.IsCramsAuthenticated,)

    project = ""
    prj_member_email = ""
    prj_lead_user_contact = ""
    action = ""
    sent_email = True  # default value

    def get_request_data(self, request):
        # try and get project and project member contact
        try:
            project_id = request.data["project_id"]
            self.action = request.data["action"]
            self.prj_member_email = request.data["email"]
            sent_email = request.data.get("sent_email")
            if type(sent_email) is bool:
                self.sent_email = sent_email

        except:
            raise exceptions.ParseError("Key error.")

        # get the action
        if self.action not in [ACCEPT, REJECT]:
            raise exceptions.ParseError("Action missing")

        # try and get the required objects
        try:
            self.project = Project.objects.get(pk=project_id)
            # check is current project
            if self.project.current_project:
                self.project = self.project.current_project

            self.prj_lead_user_contact = Contact.objects.get(
                email=request.user.email)

        except:
            raise exceptions.ParseError(
                "Can not find Project or Contact objects.")

    def is_project_leader(self):
        try:
            contact = Contact.objects.get(email=self.prj_member_email)
            first_request = self.project.requests.first()
            erb = first_request.e_research_system.e_research_body
            prj_leader_roles = ContactRole.objects.filter(
                e_research_body=erb, project_leader=True)
            prj_contacts = ProjectContact.objects.filter(
                contact=contact, contact_role__in=prj_leader_roles,
                project=self.project)
            if len(prj_contacts) != 0:
                return True
            else:
                return False
        except:
            return False

    def reject_member(self, prj_invite, user):
        # try and get existing project member contact
        try:
            contact = Contact.objects.get(email=self.prj_member_email)

            # reset the name from contact, might have been updated since
            prj_invite.given_name = contact.given_name
            prj_invite.surname = contact.surname

            delete_project_contact(rest_request=self.request,
                                   project=self.project,
                                   contact=contact,
                                   prj_jn_inv_req=prj_invite)
        except:
            # If Contact or ProjectContact doesn't exist or has been
            # removed previously, then not required to do anything else
            pass

        # update ProjectJoinInviteRequest status
        self.update_status(prj_invite, 'V', user)

    def accept_member(self, prj_invite, user):
        try:
            # create and save new project_contact
            contact = Contact.objects.get(email=self.prj_member_email)

            # reset the name from contact, might have been updated since
            prj_invite.given_name = contact.given_name
            prj_invite.surname = contact.surname

            erb = prj_invite.project.requests.first() \
                .e_research_system.e_research_body

            tm_role = ContactRole.objects.filter(
                e_research_body=erb, read_only=True).first()

            # update the ProjectJoinInviteRequest status to a member
            self.update_status(prj_invite, 'M', user, contact)

            # create project contact
            create_update_project_contact(rest_request=self.request,
                                          project=self.project,
                                          contact=contact,
                                          contact_role=tm_role,
                                          prj_jn_inv_req=prj_invite)

            return True
        except:
            return False

    def update_status(self, prj_invite, status_code, user, contact=None):
        prj_status = ProjectMemberStatus.objects.get(code=status_code)
        prj_invite.status = prj_status
        prj_invite.updated_by = user

        if contact:
            prj_invite.contact = contact

        prj_invite.save()

    def valid_email(self):
        if self.prj_member_email:
            try:
                validate_email(self.prj_member_email)
            except:
                return False
        else:
            return False

        return True

    def post(self, request):
        # get request data
        self.get_request_data(request)

        # check if user is a valid CI for project
        if not is_valid_project_lead(self.prj_lead_user_contact,
                                     self.project):
            raise exceptions.PermissionDenied(
                "Access denied, user is not a project leader or admin")

        # validate email
        if not validate_email:
            raise exceptions.ParseError("Invalid email")

        # check if contact is a member of project
        project_invites = ProjectJoinInviteRequest.objects.filter(
            project=self.project, email=self.prj_member_email)

        # get e_research_body_system from project
        erbs = get_erbs(self.project)

        if project_invites.exists():
            prj_invite = project_invites.first()

            if self.action == ACCEPT:
                # accepting member to project

                # this user is a project member
                if prj_invite.status.code == 'M':
                    raise exceptions.ParseError(
                        "User is already a project member")

                # this user has been invited to join project
                if prj_invite.status.code == 'I':
                    # Admin can accept an invite on behalf of the user
                    if not is_admin(self.prj_lead_user_contact, erbs):
                        msg = "Only admin can accept invite on user behalf"
                        raise exceptions.ParseError(msg)

                    if not self.accept_member(prj_invite, request.user):
                        raise exceptions.ParseError("Error accepting member")
                    if self.sent_email:
                        email_processing_fn = get_email_processing_fn(ERB_System_Membership_Email_fn_dict, erbs)
                        email_processing_fn(
                            subject='Project membership successful: ',
                            prj_join_invite_request=prj_invite,
                            member_status_code='M',
                            prj_lead_contacts=[self.prj_lead_user_contact],
                            erbs=erbs
                        )

                    return Response(
                        {"detail": "User accepted"},
                        status=status.HTTP_200_OK
                    )

                # this user has requested to join project
                if prj_invite.status.code == 'R':
                    # Accept user request
                    if not self.accept_member(prj_invite, request.user):
                        raise exceptions.ParseError("Error accepting member")

                    if self.sent_email:
                        email_processing_fn = get_email_processing_fn(ERB_System_Membership_Email_fn_dict, erbs)
                        email_processing_fn(
                            subject='Project membership successful: ',
                            prj_join_invite_request=prj_invite,
                            member_status_code='M',
                            prj_lead_contacts=[self.prj_lead_user_contact],
                            erbs=erbs)

                    return Response(
                        {"detail": "User accepted"},
                        status=status.HTTP_200_OK)

                # everything else
                else:
                    raise exceptions.ParseError(
                        "User has not requested to join")
            else:
                # Rejecting - declines, revokes and rejects requests

                # this user is a project member
                if prj_invite.status.code == 'M':
                    # check if member is a project leader
                    if self.is_project_leader():
                        # Only admin can remove project leader
                        if not is_admin(self.prj_lead_user_contact, erbs):
                            raise exceptions.ParseError(
                                "Can not remove a project leader from project")
                        else:
                            # check project leader being removed by admin is
                            # not the last project leader in the project

                            # get all the contacts(members) in project
                            project_contacts = ProjectContact.objects.filter(
                                project=self.project)

                            # filter project_contacts for project leader roles
                            project_leader_roles = ContactRole.objects.filter(
                                e_research_body=erbs.e_research_body,
                                project_leader=True)

                            # get all the project leader roles in erb
                            prj_lead_contacts = project_contacts.filter(
                                contact_role__in=project_leader_roles)

                            # if exactly 1 project leader left in project
                            if len(prj_lead_contacts) == 1:
                                raise exceptions.ParseError(
                                    "Can not remove the last project leader "
                                    "from project")

                    # remove member from project contact
                    self.reject_member(prj_invite, request.user)

                    if self.sent_email:
                        email_processing_fn = get_email_processing_fn(ERB_System_Membership_Email_fn_dict, erbs)
                        email_processing_fn(
                            subject='Membership Revoked: ',
                            prj_join_invite_request=prj_invite,
                            member_status_code='V',
                            prj_lead_contacts=[self.prj_lead_user_contact],
                            erbs=erbs)

                    return Response(
                        {"detail": "User project membership revoked."},
                        status=status.HTTP_200_OK)

                # this user has been invited to join project
                if prj_invite.status.code == 'I':
                    # CI or admin has cancelled the invitation to project
                    self.update_status(prj_invite,
                                       'C', request.user)

                    if self.sent_email:
                        email_processing_fn = get_email_processing_fn(ERB_System_Membership_Email_fn_dict, erbs)
                        email_processing_fn(subject='Project invite declined: ',
                                            prj_join_invite_request=prj_invite,
                                            member_status_code='C',
                                            prj_lead_contacts=[
                                                self.prj_lead_user_contact],
                                            erbs=erbs)
                    return Response(
                        {"detail": "User invitation declined."},
                        status=status.HTTP_200_OK)

                # this user has requested to join project
                if project_invites.first().status.code == 'R':
                    # reject user request to the project
                    self.update_status(prj_invite,
                                       'E', request.user)

                    if self.sent_email:
                        email_processing_fn = get_email_processing_fn(ERB_System_Membership_Email_fn_dict, erbs)
                        email_processing_fn(subject='Project request declined: ',
                                            prj_join_invite_request=prj_invite,
                                            member_status_code='E',
                                            prj_lead_contacts=[
                                                self.prj_lead_user_contact],
                                            erbs=erbs)

                    return Response(
                        {"detail": "User request has been rejected."},
                        status=status.HTTP_200_OK)

                # this user has been rejected/removed from project
                if prj_invite.status.code == 'E':
                    msg = "User has already rejected request to join."
                    return Response(
                        {"detail": msg},
                        status=status.HTTP_200_OK)

                # this user was invited but has declined to join project
                if prj_invite.status.code == 'D':
                    return Response(
                        {"detail": "User has already declined to join."},
                        status=status.HTTP_200_OK)
                
                # this user was invited an admin has canncelled the invite
                if prj_invite.status.code == 'C':
                    return Response(
                        {"detail": "User invite has been cancelled."},
                        status=status.HTTP_200_OK)

                # this user was a member but their membership has been revoked
                if prj_invite.status.code == 'V':
                    msg = "User membership has already been revoked."
                    return Response(
                        {"detail": msg},
                        status=status.HTTP_200_OK)

                # this user has cancelled their request to join the project
                if prj_invite.status.cide == 'L':
                    msg = "User has already cancelled their request to join."
                    return Response(
                        {"detail": msg},
                        status=status.HTTP_200_OK)
        else:
            raise exceptions.ParseError(
                "User: " + self.prj_lead_user_contact.email
                + " is not a project member.")


class ProjectMemberRequestViewSet(APIView):
    """
    class ProjectMemberRequestViewSet
        User accepts or rejects request to join project
    """
    permission_classes = (permissions.IsCramsAuthenticated,)

    project = ''
    prj_jn_inv_req = ''
    member_status = ''
    action = ''
    prj_lead_contact = ''

    def get_request_data(self, request):
        # try and get project
        try:
            project_id = request.data["project_id"]
            self.project = Project.objects.get(pk=project_id)
            if self.project.current_project:
                self.project = self.project.current_project
            self.action = request.data["action"]

            # if email is in the dict then this is an admin
            # accepting/rejecting on user behalf
            if 'email' in request.data:
                # first check that they are admin
                user_contact = Contact.objects.get(email=request.user.email)
                erbs = get_erbs(self.project)

                if not is_admin(user_contact, erbs):
                    raise exceptions.ParseError("You are not admin and can "
                                                "not accept or reject a "
                                                "request on behalf of a user")
                else:
                    # get the ProjectJoinInviteRequest using email from request
                    # instead of the user email
                    self.prj_jn_inv_req = ProjectJoinInviteRequest.objects.get(
                        project=self.project, email=request.data['email'])
            else:
                self.prj_jn_inv_req = ProjectJoinInviteRequest.objects.get(
                    project=self.project, email=request.user.email)

            if not self.action in [ACCEPT, REJECT]:
                raise exceptions.ParseError("Missing 'action' field")

            # get user who sent invite
            if self.prj_jn_inv_req.updated_by:
                self.prj_lead_contact = Contact.objects.get(
                    email=self.prj_jn_inv_req.updated_by.email)
            else:
                self.prj_lead_contact = Contact.objects.get(
                    email=self.prj_jn_inv_req.created_by.email)

            # member_status of project
            self.member_status = self.prj_jn_inv_req.status

        except:
            raise exceptions.ParseError("Couldn't find project id or " +
                                        "user has not been associated " +
                                        "with this project")

    def is_user_invited_requested(self):
        # user is declining their invite to join project
        if self.member_status.code == 'I':
            return True

        # user is cancelling their requested to join project
        if self.member_status.code == 'R':
            return True

        # if project member status is neither of the above return False
        return False

    def accept_invite(self, user):
        # set ProjectJoinInviteRequest status to join
        member_status = ProjectMemberStatus.objects.get(code='M')

        # get user contact
        user_contact = Contact.objects.get(email=user.email)

        # reset the name from contact, might have been updated since
        self.prj_jn_inv_req.given_name = user_contact.given_name
        self.prj_jn_inv_req.surname = user_contact.surname

        self.prj_jn_inv_req.status = member_status
        self.prj_jn_inv_req.updated_by = user
        self.prj_jn_inv_req.contact = user_contact

        erb = self.project.requests.first().e_research_system.e_research_body

        # This query gets a ERB base user/contact role that should be
        # read only. If multiple read only contact roles in an ERB then
        # the first contact role will be used
        tm_role = ContactRole.objects.filter(
            e_research_body=erb, read_only=True).first()

        # add contact to ProjectContact
        create_update_project_contact(rest_request=self.request,
                                      project=self.project,
                                      contact=user_contact,
                                      contact_role=tm_role,
                                      prj_jn_inv_req=self.prj_jn_inv_req)

    def decline_invite_request(self, user):
        # user is declining their invite to join project
        if self.member_status.code == 'I':
            new_member_status = ProjectMemberStatus.objects.get(code='D')

        # user is cancelling their requested to join project
        else:
            new_member_status = ProjectMemberStatus.objects.get(code='L')

        # save the prj_jn_inv_req changes
        self.prj_jn_inv_req.status = new_member_status
        self.prj_jn_inv_req.updated_by = user
        self.prj_jn_inv_req.save()

    def send_notification(self):
        # get e_research_body_system from project
        erbs = get_erbs(self.project)
        if self.action == ACCEPT:
            # send notifications - admin and user
            email_processing_fn = get_email_processing_fn(ERB_System_Membership_Email_fn_dict, erbs)
            email_processing_fn(subject='Invite Accepted: ',
                                prj_join_invite_request=self.prj_jn_inv_req,
                                member_status_code='M',
                                prj_lead_contacts=[self.prj_lead_contact],
                                erbs=erbs)
        else:
            # user declined CI invite
            if self.member_status.code == 'I':
                # project leader who invited user to join
                project_lead_contacts = [self.prj_lead_contact]
                subject = 'Project invite declined: '
                status_code = 'D'

            # user declined their own request
            else:
                # leave project lead contacts empty,
                # to use template default description
                project_lead_contacts = []
                subject = 'Project request declined: '
                status_code = 'L'

            email_processing_fn = get_email_processing_fn(ERB_System_Membership_Email_fn_dict, erbs)
            email_processing_fn(subject=subject,
                                prj_join_invite_request=self.prj_jn_inv_req,
                                member_status_code=status_code,
                                prj_lead_contacts=project_lead_contacts,
                                erbs=erbs)

    def post(self, request):
        # get request data
        self.get_request_data(request)

        # check if user is invited to project or has requested to join
        if not self.is_user_invited_requested():
            raise exceptions.ParseError("User is not invited or has " +
                                        "requested to join this project")

        if self.action == ACCEPT:
            # accept the invite
            self.accept_invite(request.user)
            message = "Invite/Request has been accepted"
        else:
            # decline the invite or cancel the user request
            self.decline_invite_request(request.user)
            message = "Invite/Request has been declined"

        self.send_notification()

        return Response({"detail": message},
                        status=status.HTTP_200_OK)


class ProjectMemberJoinViewSet(APIView):
    """
    class ProjectMemberJoinViewSet
        User requests to join a project
    """
    permission_classes = (permissions.IsCramsAuthenticated,)

    project = ''
    prj_jn_inv_req = ''

    def get_request_data(self, request):
        # try and get project
        try:
            project_id = request.data["project_id"]
            self.project = Project.objects.get(pk=project_id)
            if self.project.current_project:
                self.project = self.project.current_project
            return True
        except:
            return False

    def is_user_existing_project_member(self, email):
        # checks if user is already a project member, has been
        # invited or has already requested to join project

        self.prj_jn_inv_req = ProjectJoinInviteRequest.objects.filter(
            project=self.project, email=email).first()

        if self.prj_jn_inv_req:
            if self.prj_jn_inv_req.status.code == 'I':
                # user already been invited to join
                return True

            if self.prj_jn_inv_req.status.code == 'R':
                # user already requested to join
                return True

            if self.prj_jn_inv_req.status.code == 'M':
                # user already a member of project
                return True

        return False

    def join_request(self, user):
        # get user contact
        contact = Contact.objects.get(email=user.email)

        if not self.prj_jn_inv_req:
            self.prj_jn_inv_req = ProjectJoinInviteRequest()
            self.prj_jn_inv_req.project = self.project
            self.prj_jn_inv_req.created_by = user
        else:
            self.prj_jn_inv_req.updated_by = user

        # update invite details with contact
        self.prj_jn_inv_req.title = contact.title
        self.prj_jn_inv_req.surname = contact.surname
        self.prj_jn_inv_req.given_name = contact.given_name
        self.prj_jn_inv_req.email = user.email

        # get requested project member status
        req_status = ProjectMemberStatus.objects.get(code='R')
        self.prj_jn_inv_req.status = req_status
        self.prj_jn_inv_req.save()

    def send_notification(self):
        erbs = get_erbs(self.project)

        # get all project leaders for project
        prj_contacts = ProjectContact.objects.filter(
            contact_role__project_leader=True,
            project=self.project)

        prj_lead_contacts = []
        for prj_contact in prj_contacts:
            prj_lead_contacts.append(prj_contact.contact)

        email_processing_fn = get_email_processing_fn(ERB_System_Membership_Email_fn_dict, erbs)
        email_processing_fn(subject='Request to join Project: ',
                            prj_join_invite_request=self.prj_jn_inv_req,
                            member_status_code='R',
                            prj_lead_contacts=prj_lead_contacts,
                            erbs=erbs)

    def post(self, request):
        # get requested data
        if not self.get_request_data(request):
            raise exceptions.ParseError("Couldn't find project id")

        # check if user has been invited, requested or existing an member
        if self.is_user_existing_project_member(request.user.email):
            raise exceptions.ParseError("Unable to join project, user is "
                                        "either already being invited, " +
                                        "requested or is an existing " +
                                        "member of the project")

        # request to join
        self.join_request(request.user)

        # send notification to project leader
        self.send_notification()

        return Response({"detail": "Request to join success"},
                        status=status.HTTP_200_OK)


class ProjectMemberLeaveViewSet(APIView):
    """
    class ProjectMemberLeaveViewSet
        User leaves a project
    """
    permission_classes = (permissions.IsCramsAuthenticated,)

    user_contact = ''
    project = ''
    project_contacts = ''
    prj_jn_inv_req = ''

    def get_request_data(self, request):
        try:
            # get project
            project_id = request.data["project_id"]
            self.project = Project.objects.get(pk=project_id)
            if self.project.current_project:
                self.project = self.project.current_project

            # user contact
            user_email = request.user.email
            self.user_contact = Contact.objects.get(email=user_email)

        except:
            raise exceptions.ParseError("Couldn't find project id or " +
                                        "user has not been associated " +
                                        "with this project")

    def check_membership(self):
        # get the ProjectJoinInviteRequest for user and project
        self.prj_jn_inv_req = ProjectJoinInviteRequest.objects.filter(
            email=self.user_contact.email, project=self.project).first()

        # if result is empty, then user is not a member
        if not self.prj_jn_inv_req:
            raise exceptions.ParseError("User is not a member of project")

        if self.prj_jn_inv_req.status.code != 'M':
            raise exceptions.ParseError("User is not a member of project")

        # check if user is the applicant or a project leader
        self.project_contacts = ProjectContact.objects.filter(
            contact=self.user_contact, project=self.project)

        for prj_contact in self.project_contacts:
            # Applicant can not leave project
            if prj_contact.contact_role.name == db.APPLICANT:
                raise exceptions.ParseError(
                    "Applicant can not leave the project")

            # Project leader can not leave the project
            if prj_contact.contact_role.project_leader:
                raise exceptions.ParseError(
                    "Project leader can not leave the project")

    def remove_user_from_project(self):
        # change the status to revoked
        revoked = ProjectMemberStatus.objects.get(code='V')
        self.prj_jn_inv_req.status = revoked

        # reset the name from contact, might have been updated since
        self.prj_jn_inv_req.given_name = self.user_contact.given_name
        self.prj_jn_inv_req.surname = self.user_contact.surname

        # remove project contact
        delete_project_contact(rest_request=self.request,
                               project=self.project,
                               contact=self.user_contact,
                               prj_jn_inv_req=self.prj_jn_inv_req)

    def send_notification(self, request):
        erbs = get_erbs(self.project)

        # get all project leaders for project
        prj_contacts = ProjectContact.objects.filter(
            contact_role__project_leader=True,
            project=self.project)

        prj_lead_contacts = []
        for prj_contact in prj_contacts:
            prj_lead_contacts.append(prj_contact.contact)

        email_processing_fn = get_email_processing_fn(ERB_System_Membership_Email_fn_dict, erbs)
        email_processing_fn(subject='Membership revoked: ',
                            prj_join_invite_request=self.prj_jn_inv_req,
                            member_status_code='V',
                            prj_lead_contacts=prj_lead_contacts,
                            erbs=erbs)

    def post(self, request):
        project_id = request.data["project_id"]

        # get project from the project id
        self.get_request_data(request)

        # check user is a member of that project
        # raises exceptions if invalid
        self.check_membership()

        # remove the user from the project
        self.remove_user_from_project()

        # send out notification
        self.send_notification(request)

        return Response({"detail": "User removed"},
                        status=status.HTTP_200_OK)
