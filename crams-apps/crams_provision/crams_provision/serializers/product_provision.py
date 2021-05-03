import logging

from crams.models import ProvisionDetails
from crams.serializers import model_serializers
from crams.serializers.lookup_serializers import EResearchSystemSerializer
from crams_allocation.constants.db import REQUEST_STATUS_APPROVED, REQUEST_STATUS_LEGACY_APPROVED
from crams_allocation.models import Request
from crams_allocation.product_allocation.models import StorageRequest, ComputeRequest
from crams_allocation.product_allocation.serializers import compute_request
from crams_allocation.product_allocation.serializers import storage_request_serializers
from crams_allocation.serializers.question_serializers import RequestQResponseSerializer
from crams_collection.models import Project
from crams_collection.serializers.project_id_serializer import ERBProjectIDSerializer
from crams_collection.serializers.question_serializers import ProjectQResponseSerializer
from django.db.models import Q
from rest_framework import exceptions
from rest_framework import serializers

from crams_provision.serializers.base import BaseProvisionSerializer
from crams_provision.log.provision_log import ProvisionMetaLogger
from crams_provision.utils import provision_utils
from crams_provision.utils.product_utils import BaseProvisionProductUtils

LOG = logging.getLogger(__name__)


PROVISION_ENABLE_REQUEST_STATUS = [
    REQUEST_STATUS_APPROVED, REQUEST_STATUS_LEGACY_APPROVED]


def reset_provision_details(product_request):
    status_code = product_request.request.request_status.code
    if status_code == REQUEST_STATUS_APPROVED:
        if isinstance(product_request, StorageRequest):
            if product_request.approved_quota_change != 0:
                return True
    return False


class ComputeRequestProvisionSerializer(compute_request.ComputeRequestSerializer):
    provisioned = serializers.SerializerMethodField()

    message = serializers.CharField(required=False)

    class Meta(object):
        model = ComputeRequest
        fields = ['compute_product', 'compute_question_responses', 'instances',
                  'approved_instances', 'cores', 'approved_cores',
                  'core_hours', 'approved_core_hours', 'provisioned',
                  'id', 'message']
        read_only_fields = ['compute_product', 'compute_question_responses',
                            'instances', 'approved_instances', 'cores',
                            'approved_cores', 'core_hours',
                            'approved_core_hours']

    def get_provisioned(self, cr_obj):
        return BaseProvisionSerializer.get_provisioned(cr_obj, self.get_current_user())

    def validate(self, attrs):
        if not self.instance:
            pk = self.initial_data.get('id')
            self.instance = BaseProvisionProductUtils.fetch_instance(pk=pk, model=self.Meta.model)

        # validate product provisioner privilege
        current_user = self.get_current_user()
        product = attrs.get('compute_product')
        BaseProvisionProductUtils.validate_product_permission(product, current_user)
        in_provisioned_status = self.initial_data.get('provisioned', None)
        provisioned = BaseProvisionProductUtils.validate_provisioned(provisioned_status=in_provisioned_status, instance=self.instance)
        if provisioned:
            attrs['provisioned'] = provisioned
        return attrs

    def create(self, validated_data):
        msg = 'Create not allowed during provision process'
        raise exceptions.ValidationError(msg)

    def update_provisionable(self, instance, validated_data):
        current_user = self.get_current_user()
        BaseProvisionProductUtils.update_provisionable_item(instance, validated_data=validated_data, user_obj=current_user)
        return BaseProvisionProductUtils.update_request_status(instance.request, sz_context_obj=self.context)


class StorageRequestProvisionSerializer(storage_request_serializers.StorageRequestSerializer):
    provisioned = serializers.SerializerMethodField()

    message = serializers.CharField(required=False)

    # project_ids = serializers.SerializerMethodField()

    class Meta(object):
        model = StorageRequest
        fields = ['current_quota', 'storage_product', 'provision_id',
                  'requested_quota_change', 'requested_quota_total',
                  'approved_quota_change', 'approved_quota_total',
                  'storage_question_responses', 'provisioned', 'message', 'id']
        read_only_fields = ['current_quota', 'requested_quota_change',
                            'approved_quota_change']
    # TODO
    # def get_project_ids(self, sr_obj):
    #     project = sr_obj.request.project
    #     erb = sr_obj.request.e_research_system.e_research_body
    #     qs = project.archive_project_ids.filter(
    #         parent_erb_project_id__isnull=True, system__e_research_body=erb)
    #     if qs.exists:
    #         sz = projectid_contact_provision.ProvisionProjectIDSerializer
    #         return sz(qs, many=True, context=self.context).data
    #     return list()

    def get_provisioned(self, sr_obj):
        return BaseProvisionSerializer.get_provisioned(sr_obj, self.get_current_user())

    def validate_common(self, attrs):
        if not self.instance:
            pk = self.initial_data.get('id')
            self.instance = BaseProvisionProductUtils.fetch_instance(pk=pk, model=self.Meta.model)
            if self.instance.request.current_request:
                raise exceptions.ValidationError('Parent Request is not current, cannot update Storage Request')

        # validate product provisioner privilege
        current_user = self.get_current_user()
        product = attrs.get('storage_product')
        BaseProvisionProductUtils.validate_product_permission(product, current_user)
        return attrs

    def validate(self, attrs):
        attrs = self.validate_common(attrs)
        in_provisioned_status = self.initial_data.get('provisioned', None)
        provisioned = BaseProvisionProductUtils.validate_provisioned(
            provisioned_status=in_provisioned_status, instance=self.instance)
        if provisioned:
            attrs['provisioned'] = provisioned
        return attrs

    def create(self, validated_data):
        msg = 'Create not allowed during provision process'
        raise exceptions.ValidationError(msg)

    def update_provisionable(self, instance, validated_data):
        current_user = self.get_current_user()
        BaseProvisionProductUtils.update_provisionable_item(instance, validated_data, current_user)
        return BaseProvisionProductUtils.update_request_status(instance.request, sz_context_obj=self.context)


class StorageRequestProvisionIdUpdateSerializer(StorageRequestProvisionSerializer):
    provision_id = serializers.CharField(source='provision_id.provision_id')

    class Meta(object):
        model = StorageRequest
        fields = ['storage_product', 'provision_id', 'id']
        read_only_fields = ['current_quota', 'storage_product', 'requested_quota_change',
                            'requested_quota_total', 'approved_quota_change', 'project_ids',
                            'approved_quota_total', 'storage_question_responses',
                            'provisioned']

    def validate_provision_id(self, provision_id):
        if not provision_id:
            raise exceptions.ValidationError('Provision id is required')
        return provision_utils.validate_current_use_return_provision_id(provision_id, self.instance)

    def validate(self, attrs):
        return super().validate_common(attrs)

    def create(self, validated_data):
        raise exceptions.ValidationError('Create not allowed')

    def update(self, instance, validated_data):
        provision_id_obj = validated_data.get('provision_id').get('provision_id', None)

        if not instance.provision_id == provision_id_obj:
            prev_provision_id = instance.provision_id
            instance.provision_id = provision_id_obj
            instance.save()
            user_obj = self.get_current_user()
            ProvisionMetaLogger.log_provision_id_change(instance, prev_provision_id, user_obj=user_obj)

        if instance.request.request_status.code == REQUEST_STATUS_APPROVED:
            # update request_status and provision_status
            validated_data['provisioned'] = True
            super().update_provisionable(instance, validated_data)

        return instance


class ProvisionRequestSerializer(model_serializers.ReadOnlyModelSerializer):
    """class ProvisionRequestSerializer."""

    request_status = serializers.SerializerMethodField()

    e_research_system = EResearchSystemSerializer(
        required=False, allow_null=True)

    request_question_responses = serializers.SerializerMethodField()

    compute_requests = ComputeRequestProvisionSerializer(many=True, read_only=True)

    storage_requests = StorageRequestProvisionSerializer(many=True, read_only=True)

    project = serializers.SerializerMethodField()

    provisioned = serializers.SerializerMethodField()

    message = serializers.CharField(required=False)

    class Meta(object):
        model = Request
        fields = ['e_research_system', 'request_status',
                  'request_question_responses', 'compute_requests',
                  'storage_requests', 'project']

    def valid_request_erb(self, request_obj):
        if not self.context:
            return False
        valid_erb_list = self.context.get('valid_erb_list', list())
        return request_obj.e_research_system.e_research_body in valid_erb_list

    def get_request_status(self, request_obj):
        if self.valid_request_erb(request_obj):
            return request_obj.request_status.status

    def get_request_question_responses(self, request_obj):
        sz = RequestQResponseSerializer
        if self.valid_request_erb(request_obj):
            return sz(request_obj.request_question_responses, many=True).data

    def get_project(self, request_obj):
        class MinInnerSerializer(model_serializers.ReadOnlyModelSerializer):
            class Meta(object):
                model = Project
                fields = ['id', 'title']

        class MaxInnerSerializer(model_serializers.ReadOnlyModelSerializer):
            project_ids = serializers.SerializerMethodField()

            project_question_responses = serializers.SerializerMethodField()

            class Meta(object):
                model = Project
                fields = ['id', 'title',
                          'project_question_responses', 'project_ids']

            @classmethod
            def get_project_question_responses(cls, project):
                q_sz = ProjectQResponseSerializer(
                    project.project_question_responses, many=True)
                return q_sz.data

            def get_project_ids(self, project):
                if project.project_ids and self.context:
                    valid_erb_list = self.context.get('valid_erb_list')
                    if valid_erb_list:
                        id_sz = ERBProjectIDSerializer
                        project_ids = project.project_ids.filter(
                            system__e_research_body__in=valid_erb_list)
                        return id_sz(project_ids, many=True).data
                return None

        sz = MinInnerSerializer
        if self.valid_request_erb(request_obj):
            sz = MaxInnerSerializer
        return sz(request_obj.project, context=self.context).data

    @classmethod
    def build_provision_request_list_json(cls, valid_erb_list):
        context = {'valid_erb_list': valid_erb_list}
        qs = Request.objects.filter(
            e_research_system__e_research_body__in=valid_erb_list,
            request_status__code__in=PROVISION_ENABLE_REQUEST_STATUS)

        valid_req_list = list()
        if qs.exists():
            valid_status = ProvisionDetails.READY_TO_SEND_SET | \
                           ProvisionDetails.SET_OF_SENT
            filter_qs = Q(provision_details__isnull=True) | Q(
                provision_details__status__in=valid_status)
            for req in qs.all():
                if req.storage_requests and \
                        req.storage_requests.filter(filter_qs).exists():
                    valid_req_list.append(req)
                elif req.compute_requests and \
                        req.compute_requests.filter(filter_qs).exists():
                    valid_req_list.append(req)
        return cls(valid_req_list, many=True, context=context).data
