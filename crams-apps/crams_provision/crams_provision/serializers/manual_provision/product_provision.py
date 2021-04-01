# coding=utf-8
"""

"""

import logging

from django.db import transaction
from django.db.models import Q
# from rest_framework import exceptions
# from rest_framework import serializers


from crams import models
from crams_allocation.product_allocation.models import StorageRequest
from crams_allocation.constants.db import REQUEST_STATUS_APPROVED, REQUEST_STATUS_LEGACY_APPROVED
# from crams.utils.role import AbstractCramsRoleUtils
# from crams.common.utils import allocation_notification, user_utils
# from crams.common.serializers import lookup_serializers
# from crams.common.serializers import project_id_serializers
# from crams.common.serializers import model_serializers
# from crams.common.serializers import compute_request_serializers
# from crams.common.serializers import question_serializers
# from crams.common.serializers import storage_request_serializers
# from crams.provision import utils as provision_utils
# from crams.provision.serializers import projectid_contact_provision
# from crams.provision.serializers import base

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


# class BaseProvisionProductSZ(base.BaseProvisionSerializer):
#
#     provisioned = serializers.SerializerMethodField()
#
#     message = serializers.CharField(required=False)
#
#     class Meta(object):
#         model = models.ProvisionableItem
#         fields = ('provisioned', 'message')
#
#     def get_provisioned(self, obj):
#         return super().get_provisioned(obj, self.get_current_user())
#
#     def _init_empty(self, str, num):
#         ret_dict = super()._init_empty(str, num)
#         ret_dict['provisioned'] = False
#         return ret_dict
#
#     def _initFromBaseIdData(self, id):
#         ret_dict = super()._initFromBaseIdData(id)
#         ret_dict['provisioned'] = False
#         return ret_dict
#
#     def fetch_instance(self):
#         pk = self.initial_data.get('id')
#         if pk:
#             try:
#                 return self.Meta.model.objects.get(pk=pk)
#             except self.Meta.model.DoesNotExist:
#                 msg = '{} does not exists for id {}'
#                 raise exceptions.ValidationError(
#                     msg.format(self.Meta.model.__name__, pk))
#         return None
#
#     def validate_provisioned(self):
#         provisioned = self.initial_data.get('provisioned', None)
#         msg_param = 'product request'
#         super().validate_provisioned(
#             provisioned, self.instance, msg_param, False, False)
#         if self.instance:
#             return provisioned
#
#     def validate_product_permission(self, product, user_obj):
#         roles_dict = roleUtils.fetch_cramstoken_roles_dict(user_obj)
#         provider_roles = roles_dict.get(roleUtils.PROVIDER_ROLE_KEY)
#         if provider_roles and product.provider:
#             if product.provider.provider_role in provider_roles:
#                 return True
#         msg = 'User does not have permission to Provision product'
#         raise exceptions.ValidationError(msg)
#
#     @classmethod
#     def get_request_status_obj_for_code(cls, code):
#         try:
#             return models.RequestStatus.objects.get(code=code)
#         except models.RequestStatus.DoesNotExist:
#             msg = 'Request status {} does not exist'
#             raise exceptions.ValidationError(msg.format(code))
#
#     @classmethod
#     def update_request_status(cls, request_obj, serializer_context):
#         if not request_obj.request_status.code == db.REQUEST_STATUS_APPROVED:
#             msg = 'Cannot update status for non Approved Requests'
#             raise exceptions.ValidationError(msg)
#         valid_status = models.ProvisionDetails.PROVISIONED
#         filter_qs = Q(provision_details__status=valid_status)
#
#         sr_qs = request_obj.storage_requests.exclude(filter_qs)
#         cr_qs = request_obj.compute_requests.exclude(filter_qs)
#         if sr_qs.exists() or cr_qs.exists():
#             # check partial provision email send
#             notify_cls = allocation_notification.AllocationNotificationUtils
#             notify_cls.send_partial_provision_notification(
#                 request_obj, serializer_context)
#             return
#
#         # update request status to provisioned
#         request_obj.request_status = \
#             cls.get_request_status_obj_for_code(db.REQUEST_STATUS_PROVISIONED)
#         request_obj.save()
#
#     @transaction.atomic
#     def update(self, instance, validated_data, user_obj):
#         pd = super().build_new_provision_details(
#             instance, validated_data, user_obj)
#         pd.save()
#         if instance.provision_details:
#             old_pd = instance.provision_details
#             old_pd.parent_provision_details = pd
#             old_pd.updated_by = user_obj
#             old_pd.save()
#         instance.provision_details = pd
#         instance.save()
#         self.update_request_status(instance.request, self.context)
#         return instance
#
#
# SZ_CLS = compute_request_serializers.ComputeRequestSerializer
#
#
# class ComputeRequestProvisionSerializer(BaseProvisionProductSZ, SZ_CLS):
#     provisioned = serializers.SerializerMethodField()
#
#     message = serializers.CharField(required=False)
#
#     class Meta(object):
#         model = models.ComputeRequest
#         fields = ['compute_product', 'compute_question_responses', 'instances',
#                   'approved_instances', 'cores', 'approved_cores',
#                   'core_hours', 'approved_core_hours', 'provisioned',
#                   'id', 'message']
#         read_only_fields = ['compute_product', 'compute_question_responses',
#                             'instances', 'approved_instances', 'cores',
#                             'approved_cores', 'core_hours',
#                             'approved_core_hours']
#
#     def validate(self, attrs):
#         if not self.instance:
#             self.instance = self.fetch_instance()
#
#         # validate product provisioner privilege
#         current_user = self.get_current_user()
#         product = attrs.get('compute_product')
#         self.validate_product_permission(product, current_user)
#
#         provisioned = self.validate_provisioned()
#         if provisioned:
#             attrs['provisioned'] = provisioned
#         return attrs
#
#     def create(self, validated_data):
#         msg = 'Create not allowed during provision process'
#         raise exceptions.ValidationError(msg)
#
#     def update(self, instance, validated_data):
#         current_user = self.get_current_user()
#         return super().update(instance, validated_data, current_user)
#
#
# SZ_CLS = storage_request_serializers.StorageRequestSerializer
#
#
# class StorageRequestProvisionSerializer(BaseProvisionProductSZ, SZ_CLS):
#     provisioned = serializers.SerializerMethodField()
#
#     message = serializers.CharField(required=False)
#
#     project_ids = serializers.SerializerMethodField()
#
#     class Meta(object):
#         model = models.StorageRequest
#         fields = ['current_quota', 'storage_product', 'provision_id',
#                   'requested_quota_change', 'requested_quota_total',
#                   'approved_quota_change', 'approved_quota_total', 'project_ids',
#                   'storage_question_responses', 'provisioned', 'message', 'id']
#         read_only_fields = ['current_quota', 'requested_quota_change',
#                             'approved_quota_change']
#
#     @classmethod
#     def get_project_ids(cls, sr_obj):
#         project = sr_obj.request.project
#         erb = sr_obj.request.e_research_system.e_research_body
#         qs = project.archive_project_ids.filter(
#             parent_erb_project_id__isnull=True, system__e_research_body=erb)
#         if qs.exists:
#             sz = projectid_contact_provision.ProvisionProjectIDSerializer
#             return sz(qs, many=True).data
#         return list()
#
#     def validate_common(self, attrs):
#         if not self.instance:
#             self.instance = self.fetch_instance()
#             if self.instance.request.current_request:
#                 raise exceptions.ValidationError('Parent Request is not current, cannot update Storage Request')
#
#         # validate product provisioner privilege
#         current_user = self.get_current_user()
#         product = attrs.get('storage_product')
#         self.validate_product_permission(product, current_user)
#         return attrs
#
#     def validate(self, attrs):
#         attrs = self.validate_common(attrs)
#         provisioned = self.validate_provisioned()
#         if provisioned:
#             attrs['provisioned'] = provisioned
#         return attrs
#
#     def create(self, validated_data):
#         msg = 'Create not allowed during provision process'
#         raise exceptions.ValidationError(msg)
#
#     def update(self, instance, validated_data):
#         current_user = self.get_current_user()
#         return super().update(instance, validated_data, current_user)
#
#
# class StorageRequestProvisionIdUpdateSerializer(StorageRequestProvisionSerializer):
#     provision_id = serializers.CharField(source='provision_id.provision_id')
#
#     class Meta(object):
#         model = models.StorageRequest
#         fields = ['storage_product', 'provision_id', 'id']
#         read_only_fields = ['current_quota', 'storage_product', 'requested_quota_change',
#                             'requested_quota_total', 'approved_quota_change', 'project_ids',
#                             'approved_quota_total', 'storage_question_responses',
#                             'provisioned']
#
#     def validate_provision_id(self, provision_id):
#         if not provision_id:
#             raise exceptions.ValidationError('Provision id is required')
#         return provision_utils.validate_current_use_return_provision_id(provision_id, self.instance)
#
#     def validate(self, attrs):
#         return super().validate_common(attrs)
#
#     def create(self, validated_data):
#         raise exceptions.ValidationError('Create not allowed')
#
#     def update(self, instance, validated_data):
#         provision_id_obj = validated_data.get('provision_id').get('provision_id', None)
#
#         if not instance.provision_id == provision_id_obj:
#             prev_provision_id = instance.provision_id
#             instance.provision_id = provision_id_obj
#             instance.save()
#             user_obj = self.get_current_user()
#             provision_utils.log_provision_id_change(instance, prev_provision_id, user_obj=user_obj)
#
#         return instance
#
#
# class ProvisionRequestSerializer(model_serializers.ReadOnlyModelSerializer):
#     """class ProvisionRequestSerializer."""
#
#     request_status = serializers.SerializerMethodField()
#
#     e_research_system = lookup_serializers.EResearchSystemSerializer(
#         required=False, allow_null=True)
#
#     request_question_responses = serializers.SerializerMethodField()
#
#     compute_requests = ComputeRequestProvisionSerializer(many=True,
#                                                          read_only=True)
#     storage_requests = StorageRequestProvisionSerializer(many=True,
#                                                          read_only=True)
#     project = serializers.SerializerMethodField()
#
#     class Meta(object):
#         model = models.Request
#         fields = ['e_research_system', 'request_status',
#                   'request_question_responses', 'compute_requests',
#                   'storage_requests', 'project']
#
#     def valid_request_erb(self, request_obj):
#         if not self.context:
#             return False
#         valid_erb_list = self.context.get('valid_erb_list', list())
#         return request_obj.e_research_system.e_research_body in valid_erb_list
#
#     def get_request_status(self, request_obj):
#         if self.valid_request_erb(request_obj):
#             return request_obj.request_status.status
#
#     def get_request_question_responses(self, request_obj):
#         sz = question_serializers.RequestQResponseSerializer
#         if self.valid_request_erb(request_obj):
#             return sz(request_obj.request_question_responses, many=True).data
#
#     def get_project(self, request_obj):
#         class MinInnerSerializer(model_serializers.ReadOnlyModelSerializer):
#             class Meta(object):
#                 model = models.Project
#                 fields = ['id', 'title']
#
#         class MaxInnerSerializer(model_serializers.ReadOnlyModelSerializer):
#             project_ids = serializers.SerializerMethodField()
#
#             project_question_responses = serializers.SerializerMethodField()
#
#             class Meta(object):
#                 model = models.Project
#                 fields = ['id', 'title',
#                           'project_question_responses', 'project_ids']
#
#             @classmethod
#             def get_project_question_responses(cls, project):
#                 q_sz = question_serializers.ProjectQResponseSerializer(
#                     project.project_question_responses, many=True)
#                 return q_sz.data
#
#             def get_project_ids(self, project):
#                 if project.project_ids and self.context:
#                     valid_erb_list = self.context.get('valid_erb_list')
#                     if valid_erb_list:
#                         id_sz = project_id_serializers.ERBProjectIDSerializer
#                         project_ids = project.project_ids.filter(
#                             system__e_research_body__in=valid_erb_list)
#                         return id_sz(project_ids, many=True).data
#                 return None
#
#         sz = MinInnerSerializer
#         if self.valid_request_erb(request_obj):
#             sz = MaxInnerSerializer
#         return sz(request_obj.project, context=self.context).data
#
#     @classmethod
#     def build_provision_request_list_json(cls, valid_erb_list):
#         context = {'valid_erb_list': valid_erb_list}
#         qs = models.Request.objects.filter(
#             e_research_system__e_research_body__in=valid_erb_list,
#             request_status__code__in=PROVISION_ENABLE_REQUEST_STATUS)
#
#         valid_req_list = list()
#         if qs.exists():
#             valid_status = models.ProvisionDetails.READY_TO_SEND_SET | \
#                            models.ProvisionDetails.SET_OF_SENT
#             filter_qs = Q(provision_details__isnull=True) | Q(
#                 provision_details__status__in=valid_status)
#             for req in qs.all():
#                 if req.storage_requests and \
#                         req.storage_requests.filter(filter_qs).exists():
#                     valid_req_list.append(req)
#                 elif req.compute_requests and \
#                         req.compute_requests.filter(filter_qs).exists():
#                     valid_req_list.append(req)
#         return cls(valid_req_list, many=True, context=context).data
