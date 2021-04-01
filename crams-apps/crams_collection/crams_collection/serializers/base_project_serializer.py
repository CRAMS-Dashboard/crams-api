"""

"""

from rest_framework import serializers
from rest_framework.exceptions import ParseError

from crams_contact.serializers import base_contact_serializer
from crams_collection.serializers import domain_serializers
from crams_collection.serializers import grant_serializers

from crams_collection.serializers import question_serializers
from crams_contact.serializers.lookup_serializers import DepartmentFlatSerializer
from crams_contact.serializers.util_sz import CramsAPIActionStateModelSerializer
from crams_collection.serializers import publication_serializers
from crams_collection.serializers.provision_details import CollectionProvisionDetailsSerializer
from crams_collection.serializers.project_contact_serializer import ProjectContactSerializer
from crams_collection.models import Project
from crams.models import ArchivableModel


class ReadOnlyProjectSerializer(CramsAPIActionStateModelSerializer):
    """
        class ReadOnlyProjectSerializer.
    """
    # project question response
    project_question_responses = serializers.SerializerMethodField()

    # Publication
    publications = serializers.SerializerMethodField()

    # Grant information
    grants = serializers.SerializerMethodField()

    # ProjectID
    project_ids = serializers.SerializerMethodField()

    # Contacts
    project_contacts = serializers.SerializerMethodField()

    # Project Provision Details
    provision_details = serializers.SerializerMethodField(
        method_name='filter_provision_project')

    # Domains
    domains = serializers.SerializerMethodField()

    # Department
    department = DepartmentFlatSerializer(required=False, allow_null=True)

    historic = serializers.SerializerMethodField(method_name='is_historic')

    contact_system_ids = serializers.SerializerMethodField()

    readonly = serializers.SerializerMethodField()

    class Meta(object):
        """class Meta."""

        model = Project
        fields = [
            'id',
            'crams_id',
            'title',
            'description',
            'department',
            'historic',
            'notes',
            'project_question_responses',
            'publications',
            'grants',
            'project_ids',
            'project_contacts',
            'provision_details',
            'domains',
            'contact_system_ids',
            'readonly',
        ]
        read_only_fields = ['provision_details',
                            'creation_ts',
                            'last_modified_ts',
                            'contact_system_ids']

    def create(self, validated_data):
        """create.

        :param validated_data:
        :raise ParseError:
        """
        raise ParseError('Create not allowed ')

    def update(self, instance, validated_data):
        """update.

        :param instance:
        :param validated_data:
        :raise ParseError:
        """
        raise ParseError('Update not allowed ')

    @classmethod
    def get_project_question_responses(cls, project_obj):
        responses = ArchivableModel.get_current_for_qs(project_obj.project_question_responses.all())
        if responses:
            return question_serializers.ProjectQuestionResponseSerializer(responses, many=True).data
        return list()

    @classmethod
    def get_publications(cls, project_obj):
        publications = ArchivableModel.get_current_for_qs(project_obj.publications.all())
        if publications:
            return publication_serializers.PublicationSerializer(publications, many=True).data
        return list()

    @classmethod
    def get_grants(cls, project_obj):
        grants = ArchivableModel.get_current_for_qs(project_obj.grants.all())
        if grants:
            return grant_serializers.GrantSerializer(grants, many=True).data
        return list()

    @classmethod
    def get_domains(cls, project_obj):
        domains = project_obj.domains.all()
        if domains:
            return domain_serializers.DomainSerializer(domains, many=True).data
        return list()

    def get_project_contacts(self, project_obj):
        sz_class = ProjectContactSerializer
        if project_obj.project_contacts.exists():
            return sz_class(project_obj.project_contacts.all(), many=True, context=self.context).data
        return list()

    def get_readonly(self, project_obj):
        current_contact = base_contact_serializer.get_serializer_user_contact(self)
        if current_contact:
            return CramsAPIActionStateModelSerializer.project_contact_has_readonly_access(
                project_obj, current_contact)
        return True

    def get_contact_system_ids(self, project_obj):
        current_contact = base_contact_serializer.get_serializer_user_contact(self)
        qs = project_obj.project_contacts.filter(contact=current_contact)
        if not qs.exists():
            return None
        # TODO fix after Contact/Provision ID is fixed
        # sz_class = user_id_provision.ProvisionedContactSystemIdentifiers
        # return sz_class(current_contact, context=self.context).data

    @classmethod
    def get_project_ids(cls, project_obj):
        # TODO: define rules for showing project ids
        return list()
        # return ProvisionProjectIDSerializer(project_obj.project_ids.all(), many=True).data

    @staticmethod
    def is_historic(project_obj):
        return project_obj.current_project is not None

    def filter_provision_project(self, project_obj):
        """

        :param project_obj:
        :return:
        """
        if hasattr(self, 'cramsActionState'):
            user_obj = self.cramsActionState.rest_request.user
            context = CollectionProvisionDetailsSerializer.build_context_obj(user_obj)
        else:
            context = CollectionProvisionDetailsSerializer.hide_error_msg_context()

        ret_list = []
        for p in project_obj.linked_provisiondetails.all():
            pd_serializer = CollectionProvisionDetailsSerializer(p.provision_details, context=context)
            ret_list.append(pd_serializer.data)

        return ret_list
