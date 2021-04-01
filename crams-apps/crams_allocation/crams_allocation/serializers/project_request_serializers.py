# coding=utf-8
"""

"""
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, ParseError

from crams.extension.config_init import CONTACT_ROLE_VALID_COUNT
from crams.constants.api import CLONE
from crams.constants.api import OVERRIDE_READONLY_DATA
from crams_collection.constants.api import DO_NOT_SERIALIZE_REQUESTS_FOR_PROJECT
from crams_collection.models import Project
from crams_allocation.models import Request
from crams_collection.serializers.base_project_serializer import ReadOnlyProjectSerializer
from crams_collection.serializers.project_serializer import ProjectSerializer
from crams_allocation.serializers.base import ReadOnlyCramsRequestWithoutProjectSerializer
from crams_allocation.serializers.request_serializers import CramsRequestWithoutProjectSerializer

from crams_allocation.constants import db as allocation_db_constants


class CommonProjectRequestCodeBase(serializers.Serializer):
    @classmethod
    def get_crams_request_serializer_class(cls):
        return ReadOnlyCramsRequestWithoutProjectSerializer

    @classmethod
    def get_first_status_dates(cls, project_obj):
        def get_earliest_status(status_code):
            obj_qs = ph_qs.filter(request_status__code=status_code)
            if obj_qs.exists():
                return obj_qs.earliest('creation_ts').creation_ts
            return None

        if project_obj.current_project:
            return None
        req_filter = Q(project=project_obj)
        req_filter |= Q(project__current_project=project_obj)
        ph_qs = Request.objects.filter(req_filter)

        ret_dict = dict()
        ret_dict['approved'] = get_earliest_status(allocation_db_constants.REQUEST_STATUS_APPROVED)
        ret_dict['provisioned'] = get_earliest_status(allocation_db_constants.REQUEST_STATUS_PROVISIONED)
        if ret_dict['provisioned']:
            if not ret_dict['approved'] or \
                    ret_dict['provisioned'] < ret_dict['approved']:
                # vicnode migrated records has no approval date
                ret_dict['approved'] = ret_dict['provisioned']

        # ingest_date_dict = dict()
        # ret_dict['ingest'] = ingest_date_dict
        #
        # curr_requests = project_obj.requests.filter(
        #     current_request__isnull=True)
        # usage_filter = Q(ingested_gb_disk__gt=0) | Q(ingested_gb_tape__gt=0)
        # for request in curr_requests:
        #     for storage_request in request.storage_requests.all():
        #         provision_id: StorageProductProvisionId = storage_request.provision_id
        #         if not provision_id:
        #             continue
        #
        #         sp_name = storage_request.storage_product.name
        #         value_key = sp_name + '_value'
        #         # TODO  reverse relation 'ingests' to be managed
        #         ingest_date_qs = provision_id.ingests.filter(usage_filter)
        #         if ingest_date_qs.exists():
        #             earliest_ingest = ingest_date_qs.earliest('extract_date')
        #             ingest_date = earliest_ingest.extract_date
        #             ingest_value = earliest_ingest.ingested_gb_disk + earliest_ingest.ingested_gb_tape
        #             ingest_value_str = "{0:.3f}".format(ingest_value)
        #             if sp_name not in ingest_date_dict \
        #                     or ingest_date < ingest_date_dict[sp_name]:
        #                 ingest_date_dict[sp_name] = ingest_date
        #                 ingest_date_dict[value_key + '_str'] = ingest_value_str
        #                 ingest_date_dict[value_key] = ingest_value

        return ret_dict

    def filter_requests(self, project_obj):
        """filter requests.

        :param project_obj:
        :return:
        """
        # Filter project requests based on Url parameters
        # To get URL params use self.context['request'].query_params(xxx,None)
        context_request = self.context['request']
        request_id = context_request.query_params.get('request_id', None)
        if request_id:
            # , current_request__isnull=True)
            requests = project_obj.requests.filter(id=request_id)
        else:
            requests = project_obj.requests.filter(current_request__isnull=True)

        ret_list = []
        override_data = self.context.get(OVERRIDE_READONLY_DATA, None)
        serialize_requests = not (override_data and
                                  DO_NOT_SERIALIZE_REQUESTS_FOR_PROJECT in
                                  override_data)

        if serialize_requests:
            req_sz_class = self.get_crams_request_serializer_class()
            req_context = {'request': context_request}
            for req in requests:
                req_serializer = req_sz_class(req, context=req_context)
                ret_list.append(req_serializer.data)

        return ret_list


class ReadOnlyProjectRequestSerializer(ReadOnlyProjectSerializer, CommonProjectRequestCodeBase):
    # Request
    requests = serializers.SerializerMethodField(method_name='filter_requests')

    first_status_dates = serializers.SerializerMethodField()

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
            'requests',
            'readonly',
            'first_status_dates'
        ]
        read_only_fields = ['crams_id',
                            'provision_details',
                            'creation_ts',
                            'last_modified_ts',
                            'contact_system_ids']

    @classmethod
    def get_crams_request_serializer_class(cls):
        return ReadOnlyCramsRequestWithoutProjectSerializer

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


class ProjectRequestSerializer(ProjectSerializer, CommonProjectRequestCodeBase):
    # Request
    requests = serializers.SerializerMethodField(method_name='filter_requests')

    class Meta(object):
        """class Meta."""

        model = Project
        fields = [
            'id',
            'crams_id',
            'title',
            'description',
            'department',
            'notes',
            'project_question_responses',
            'publications',
            'grants',
            'project_ids',
            'project_contacts',
            'domains',
            'requests'
        ]

    @classmethod
    def get_crams_request_serializer_class(cls):
        return CramsRequestWithoutProjectSerializer

    def validate(self, data):
        data = super().validate(data)
        project_contacts = data.get('project_contacts')
        if project_contacts:
            requests = self.initial_data.get('requests')
            self.validate_contact_rules(project_contacts, requests)

        return data

    def validate_contact_rules(self, project_contacts, requests):
        def format_message(count, prefix, word=None, suffix=None):
            if word and count > 1:
                word += 's'
            return 'project_contacts: ' + prefix + ' ' + word + ' ' + suffix

        if self.cramsActionState.is_update_action:
            if not project_contacts:
                raise ValidationError(
                    format_message(0, 'A project contact is required'))

        role_count_rules = dict()
        if requests:
            for request in requests:
                erb_system_dict = request.get('e_research_system')
                if erb_system_dict and 'name' in erb_system_dict:
                    contact_role_rules = \
                        CONTACT_ROLE_VALID_COUNT.get(
                            erb_system_dict.get('name'))
                    if contact_role_rules:
                        role_count_rules.update(contact_role_rules)
        if role_count_rules:
            role_count_map = dict()
            for contact in project_contacts:
                contact_role_obj = contact.get('contact_role')
                if not contact_role_obj:
                    raise ValidationError(
                        format_message(0, 'Role value required for contact'))
                role_name = contact_role_obj.name.lower()
                counter = role_count_map.get(role_name, 0) + 1
                role_count_map[role_name] = counter

            for role, (min_count, max_count) in role_count_rules.items():
                current_count = role_count_map.get(role.lower(), 0)
                if min_count and current_count < min_count:
                    raise ValidationError(
                        format_message(min_count, 'Expected atleast {}',
                                       'contact', 'with role {}').format(
                            str(min_count), role))
                if max_count and current_count > max_count:
                    raise ValidationError(
                        format_message(max_count, 'Expected at most {}',
                                       'contact', 'with role {}').format(
                            str(max_count), role))

    def create_new_project_archive_existing(self, existing_project_instance):
        save_new, ret_requests_sz = self.validate_requests_determine_save_new(existing_project_instance)
        return save_new

    def validate_requests_determine_save_new(self, existing_project_instance):
        context = dict()
        context['request'] = self.context['request']

        requests = self.initial_data.get('requests')
        if not requests:
            raise ValidationError('Requests expected, got none')

        existing_request_instances = {}
        if existing_project_instance:
            for existing_request_instance in \
                    existing_project_instance.requests.all():
                existing_request_instances[
                    existing_request_instance.id] = existing_request_instance

        # only save a new request if save_new flag is True
        err_list = list()
        req_sz_class = self.get_crams_request_serializer_class()
        ret_requests_sz = list()
        save_new = False
        for requestData in requests:
            current_request = requestData.get('current_request', None)
            if current_request:
                # These are historic requests, should not be updated.
                continue

            request_id = requestData.get('id', None)
            if request_id:
                existing_request_instance = existing_request_instances.pop(
                    request_id, None)
                msg = 'Archived requests cannot be updated. Request Id {}'
                if existing_request_instance:
                    if existing_request_instance.current_request:
                        raise ParseError(msg.format(request_id))
                    request_serializer = req_sz_class(
                        existing_request_instance,
                        data=requestData,
                        context=context)
                else:
                    raise ParseError(
                        'Project/Request mismatch, cannot find request' +
                        ' with id {}'.format(repr(request_id)))
            else:
                request_serializer = req_sz_class(
                    data=requestData, context=context)

            request_serializer.is_valid()
            if request_serializer.errors:
                err_list.append(request_serializer.errors)
                continue
            ret_requests_sz.append(request_serializer)
            if not save_new:
                save_new |= request_serializer.validated_data.get('save_new', True)

        # TODO # copy remaining requests across
        # # request_status is read_only, hence cannot be passed in updateData
        # context[OVERRIDE_READONLY_DATA] = {CLONE: True}
        # for idKey, req_instance in existing_request_instances.items():
        #     if not req_instance.current_request:
        #         request_serializer = req_sz_class(
        #             req_instance, data={},
        #             partial=True, context=context)
        #         request_serializer.is_valid()
        #         if request_serializer.errors:
        #             err_list.append(request_serializer.errors)
        #             continue
        #         ret_requests_sz.append(request_serializer)
        #         if not save_new:
        #             save_new |= request_serializer.validated_data.get('save_new', True)

        if err_list:
            raise ValidationError(err_list)

        return save_new, ret_requests_sz

    def update_requests(self, project_data):
        project = project_data.get('project_obj')
        existing_project_instance = project_data.get('existing_project_instance')

        # Clone current project Ids to new project
        if existing_project_instance and not existing_project_instance == project:
            user_erb_roles = self.get_provision_roles_for_user()
            # TODO decide how to manage project Id clone/carry across
            # sz = ProvisionProjectIDSerializer
            # for project_id in existing_project_instance.project_ids.all():
            #     sz(project_id, context=self.context). \
            #         clone_to_new_project(project, user_erb_roles)

        requests_sz = project_data.get('requests')
        if requests_sz:
            for sz in requests_sz:
                sz.validated_data['project'] = project
                sz.save()

    def save_project(self, validated_data, existing_project_instance):
        save_new, validated_requests_sz = self.validate_requests_determine_save_new(existing_project_instance)

        print('validated data', )
        project_obj = super().save_project(
            validated_data=validated_data, existing_project_instance=existing_project_instance)

        project_data_dict = {
            'requests': validated_requests_sz,
            'existing_project_instance': existing_project_instance,
            'project_obj': project_obj
        }
        self.update_requests(project_data=project_data_dict)

        return project_obj
