from rest_framework import serializers

from crams.models import User
from crams_compute.models import ComputeProduct
from crams_allocation.product_allocation.models import ComputeRequest
from crams_contact.models import Contact
from crams.models import EResearchBodySystem
from crams_contact.models import EResearchContactIdentifier
from crams_collection.models import Project
from crams_collection.models import ProjectContact
from crams_collection.models import ProjectID
from crams_member.models import ProjectJoinInviteRequest
from crams_member.models import ProjectMemberStatus
from crams_allocation.models import Request
from crams_allocation.models import RequestStatus
from crams_storage.models import StorageProduct
from crams_allocation.product_allocation.models import StorageRequest
from crams_storage.models import StorageType


def get_project_contacts(prj_jn_inv_req):
    try:
        contact = Contact.objects.get(email=prj_jn_inv_req.email)
        prj_contacts = ProjectContact.objects.filter(
            contact=contact, project=prj_jn_inv_req.project)

        return prj_contacts
    except:
        return None


class EResearchBodySystemSerializer(serializers.ModelSerializer):
    e_research_body = serializers.SerializerMethodField()

    class Meta:
        model = EResearchBodySystem
        fields = ('name', 'e_research_body')

    def get_e_research_body(self, obj):
        return obj.e_research_body.name


class RequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestStatus


class StorageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageType


class ComputeProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputeProduct
        fields = ('id', 'name')


class ParentStorageProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageProduct
        fields = ('id', 'name')


class StorageProductSerializer(serializers.ModelSerializer):
    storage_type = StorageTypeSerializer(many=False)
    parent_storage_product = ParentStorageProductSerializer(many=False)

    class Meta:
        model = StorageProduct
        fields = ('id', 'name', 'storage_type', 'zone',
                  'parent_storage_product')


class ComputeRequestSerializer(serializers.ModelSerializer):
    compute_product = ComputeProductSerializer(many=False)

    class Meta:
        model = ComputeRequest
        fields = ('id', 'instances', 'approved_instances', 'cores',
                  'approved_cores', 'core_hours', 'approved_core_hours',
                  'compute_product')


class StorageRequestSerializer(serializers.ModelSerializer):
    storage_product = StorageProductSerializer(many=False)

    class Meta:
        model = StorageRequest
        fields = ('id', 'current_quota', 'provision_id', 'storage_product',
                  'requested_quota_change', 'requested_quota_total',
                  'approved_quota_change', 'approved_quota_total')


class RequestSerializer(serializers.ModelSerializer):
    """
    Class RequestSerializer
        This is just a subset of request it doesn't retrieve
        everything in a request like the allocation request view
    """
    request_status = RequestStatusSerializer(many=False)
    compute_requests = ComputeRequestSerializer(many=True)
    storage_requests = StorageRequestSerializer(many=True)
    e_research_system = EResearchBodySystemSerializer(many=False)

    class Meta:
        model = Request
        fields = ('id', 'request_status', 'compute_requests',
                  'storage_requests', 'e_research_system')


class ProjectSerializer(serializers.ModelSerializer):
    """
    Class ProjectSerializer
    """
    system_id = serializers.SerializerMethodField()
    requests = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'system_id', 'title', 'description',
                  'requests')

    def get_system_id(self, obj):
        try:
            project_id = ProjectID.objects.get(project=obj)
            return project_id.identifier
        except:
            return None

    def get_requests(self, obj):
        # only get requests with no current_request
        qs = Request.objects.filter(project=obj,
                                    current_request=None)
        serializer = RequestSerializer(instance=qs, many=True)

        return serializer.data


class ProjectIDSerializer(serializers.ModelSerializer):
    """
    Class ProjectIDSerializer
    """
    id = serializers.SerializerMethodField()
    e_research_systems = serializers.SerializerMethodField()
    system_id = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'e_research_systems',
                  'system_id', 'title', 'description')

    def get_id(self, obj):
        return obj.project.id

    def get_e_research_systems(self, obj):
        erb_list = []

        for request in obj.project.requests.all():
            erb_list.append(EResearchBodySystemSerializer(
                request.e_research_system).data)

        return erb_list

    def get_system_id(self, obj):
        return obj.identifier

    def get_title(self, obj):
        return obj.project.title

    def get_description(self, obj):
        return obj.project.description


class MemberDetailSerializer(serializers.ModelSerializer):
    """
    Class MemberDetailSerializer
    """
    user_id = serializers.SerializerMethodField()
    contact_id = serializers.SerializerMethodField()
    given_name = serializers.SerializerMethodField()
    surname = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    project_leader = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    status_code = serializers.SerializerMethodField()

    class Meta:
        model = ProjectJoinInviteRequest
        fields = ('user_id', 'contact_id', 'given_name', 'surname', 'email',
                  'roles', 'project_leader', 'status', 'status_code')

    def get_user_id(self, obj):
        try:
            # get eresearchbody
            erb = obj.project.requests.first() \
                .e_research_system.e_research_body

            contact = Contact.objects.get(email=obj.email)

            erc_id = EResearchContactIdentifier.objects.get(
                contact=contact,
                system__e_research_body=erb)
            return erc_id.identifier
        except:
            # no user_id found return empty
            return None

    def get_contact_id(self, obj):
        try:
            contact = Contact.objects.get(email=obj.email)

            return contact.id
        except:
            # no contact found return empty
            return None

    def get_given_name(self, obj):
        return obj.given_name

    def get_surname(self, obj):
        return obj.surname

    def get_email(self, obj):
        return obj.email

    def get_roles(self, obj):
        if obj.status.code == 'M':
            prj_contacts = get_project_contacts(obj)

            if prj_contacts:
                role_list = []
                for prj_cont in prj_contacts:
                    role_list.append(prj_cont.contact_role.name)
                return role_list

        return None

    def get_project_leader(self, obj):
        if obj.status.code == 'M':
            prj_contacts = get_project_contacts(obj)

            if prj_contacts:
                for prj_cont in prj_contacts:
                    if prj_cont.contact_role.project_leader:
                        return True
        return False

    def get_status(self, obj):
        return obj.status.status

    def get_status_code(self, obj):
        return obj.status.code


class ProjectMemberSerialzer(serializers.ModelSerializer):
    """
    class ProjectMemberSerializer
    """
    system_id = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    provision_status = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'title', 'system_id', 'provision_status', 'members')

    def get_system_id(self, obj):
        try:
            project_id = ProjectID.objects.get(project=obj)

            return project_id.identifier
        except:
            return None

    def get_project_status(self, obj):
        # get this project children
        children_projects = Project.objects.filter(current_project=obj)

        # look through child projects if they exist
        if children_projects:
            for chd_prj in children_projects:
                for req in chd_prj.requests.all():
                    if req.request_status.code == 'P':
                        return req.request_status.code

        # check all requests in current project
        for req in obj.requests.all():
            if req.request_status.code == 'P':
                return req.request_status.code

        # if provision status not found return the latest request status
        return obj.requests.all().order_by('-last_modified_ts')[0].request_status.code

    def get_provision_status(self, obj):
        return self.get_project_status(obj)

    def get_members(self, obj):
        # get project contacts if any
        prj_contacts = ProjectContact.objects.filter(project=obj)

        # get the current ProjectJoinInviteRequest list of members
        prj_jn_inv_reqs = ProjectJoinInviteRequest.objects.filter(project=obj)

        # grab all the emails in the ProjectJoinInviteRequest to check against
        # current project contacts
        prj_member_email_list = []
        for prj_jn_inv_req in prj_jn_inv_reqs:
            prj_member_email_list.append(prj_jn_inv_req.email.lower())

        # add member from the ProjectContact if they don't exist
        # in the ProjectJoinInviteRequest
        for prj_contact in prj_contacts:
            if self.get_project_status(obj) == 'P':
                provisioned = True
            else:
                provisioned = False

            if provisioned:
                if prj_contact.contact.email.lower() \
                        not in prj_member_email_list:
                    # check if prj_jn_inv_req exist for contact and project
                    existing_membership_list = \
                        ProjectJoinInviteRequest.objects.filter(
                            project=prj_contact.project,
                            email=prj_contact.contact.email)

                    # if prj_jn_inv_req found
                    if len(existing_membership_list) == 0:
                        new_member = ProjectJoinInviteRequest()
                        new_member.surname = prj_contact.contact.surname
                        new_member.given_name = prj_contact.contact.given_name
                        new_member.email = prj_contact.contact.email
                        new_member.project = prj_contact.project
                        new_member.status = \
                            ProjectMemberStatus.objects.get(code='M')
                        try:
                            new_member.created_by = User.objects.get(
                                email=prj_contact.contact.email)
                        except:
                            # user has not logged in or have been removed
                            pass
                        new_member.contact = prj_contact.contact
                        new_member.save()

        # update ProjectJoinInviteRequest if any missing members from
        # ProjectContact were added above
        prj_jn_inv_reqs = ProjectJoinInviteRequest.objects.filter(project=obj)

        return MemberDetailSerializer(prj_jn_inv_reqs, many=True).data


class ProjectMemberInviteRequestSerializer(serializers.ModelSerializer):
    """
    class ProjectMemberInviteRequestSerializer
    """
    project_id = serializers.SerializerMethodField()
    project_group_id = serializers.SerializerMethodField()
    project_title = serializers.SerializerMethodField()
    project_desc = serializers.SerializerMethodField()
    e_research_systems = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    status_code = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    user_roles = serializers.SerializerMethodField()
    authorized_by = serializers.SerializerMethodField()

    class Meta:
        model = ProjectJoinInviteRequest
        fields = ('project_id', 'project_group_id', 'project_title',
                  'project_desc', 'e_research_systems', 'status',
                  'status_code', 'date', 'user_email', 'user_roles',
                  'authorized_by')

    def get_project_id(self, obj):
        return obj.project.id

    def get_project_group_id(self, obj):
        # get the latest projectID by checking provision date
        projectIDs = ProjectID.objects.filter(
            project=obj.project).order_by('-provision_details__last_modified_ts')

        if projectIDs:
            # use the first project_id from latest provisioned project
            return projectIDs.first().identifier
        else:
            return None

    def get_project_title(self, obj):
        return obj.project.title

    def get_project_desc(self, obj):
        return obj.project.description

    def get_e_research_systems(self, obj):
        erbs_list = []

        for request in obj.project.requests.all():
            erbs_list.append(EResearchBodySystemSerializer(
                request.e_research_system).data)

        return erbs_list

    def get_status(self, obj):
        return obj.status.status

    def get_status_code(self, obj):
        return obj.status.code

    def get_date(self, obj):
        return obj.last_modified_ts

    def get_user_email(self, obj):
        user = self.context['request'].user
        return user.email

    def get_user_roles(self, obj):
        if obj.status.code == 'M':
            prj_contacts = get_project_contacts(obj)

            if prj_contacts:
                role_list = []
                for prj_cont in prj_contacts:
                    role_list.append(prj_cont.contact_role.name)
                return role_list

        return None

    def get_authorized_by(self, obj):
        if obj.updated_by:
            return obj.updated_by.email
        elif obj.created_by:
            return obj.created_by.email
        else:
            return None
