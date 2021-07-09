# coding=utf-8
"""

"""
import logging
import copy

from crams.constants.api import OVERRIDE_READONLY_DATA
from crams.models import ProvisionDetails
from crams_provision.utils.base import BaseProvisionUtils
from crams_provision.config.provision_config import ERB_System_Partial_Provision_Email_fn_dict
from crams_provision.config.provision_config import get_email_processing_fn
from crams.utils.role import AbstractCramsRoleUtils
from crams_allocation.serializers.admin_serializers import BaseAdminSerializer
from crams_allocation.constants.db import REQUEST_STATUS_APPROVED, REQUEST_STATUS_LEGACY_APPROVED
from crams_allocation.constants.db import REQUEST_STATUS_PROVISIONED
from crams_allocation.models import RequestStatus
from django.db.models import Q
from rest_framework import exceptions

LOG = logging.getLogger(__name__)

PROVISION_ENABLE_REQUEST_STATUS = [
    REQUEST_STATUS_APPROVED, REQUEST_STATUS_LEGACY_APPROVED]


class BaseProvisionProductUtils:
    @classmethod
    def fetch_instance(cls, pk, model):
        if pk:
            try:
                return model.objects.get(pk=pk)
            except model.DoesNotExist:
                msg = '{} does not exists for id {}'
                raise exceptions.ValidationError(
                    msg.format(model.__name__, pk))
        return None

    @classmethod
    def validate_provisioned(
            cls, provisioned_status, instance, msg_param='product request', is_clone=False, is_admin=False):
        BaseProvisionUtils.validate_provisioned(
            provisioned_status, instance, msg_param, False, False)
        if instance:
            return provisioned_status

    @classmethod
    def validate_product_permission(cls, product, user_obj):
        roles_dict = AbstractCramsRoleUtils.fetch_cramstoken_roles_dict(user_obj)
        provider_roles = roles_dict.get(AbstractCramsRoleUtils.PROVIDER_ROLE_KEY)
        if provider_roles and product.provider:
            if product.provider.provider_role in provider_roles:
                return True
        msg = 'User does not have permission to Provision product'
        raise exceptions.ValidationError(msg)

    @classmethod
    def get_request_status_obj_for_code(cls, code):
        try:
            return RequestStatus.objects.get(code=code)
        except RequestStatus.DoesNotExist:
            msg = 'Request status {} does not exist'
            raise exceptions.ValidationError(msg.format(code))

    @classmethod
    def update_request_status(cls, request_obj, sz_context_obj):
        if not request_obj.request_status.code == REQUEST_STATUS_APPROVED:
            msg = 'Cannot update status for non Approved Requests'
            raise exceptions.ValidationError(msg)
        valid_status = ProvisionDetails.PROVISIONED
        filter_qs = Q(provision_details__status=valid_status)

        sr_qs = request_obj.storage_requests.exclude(filter_qs)
        cr_qs = request_obj.compute_requests.exclude(filter_qs)
        update_request_status = True
        if sr_qs.exists():
            update_request_status = False
        if cr_qs.exists():
            update_request_status = False
        
        erbs = request_obj.e_research_system
        
        # send partial provisioned email
        email_processing_fn = get_email_processing_fn(ERB_System_Partial_Provision_Email_fn_dict, erbs)
        email_processing_fn(alloc_req=request_obj, serializer_context=sz_context_obj)

        if update_request_status:
            # update request status to provisioned
            # Instead of updating Approve to Provision status,
            #   - we need to use archive the current Approved Request and create a new record
            if sz_context_obj and isinstance(sz_context_obj, dict):
                partial_request_context_obj = copy.copy(sz_context_obj)
                partial_request_context_obj[OVERRIDE_READONLY_DATA] = {'request_status': REQUEST_STATUS_PROVISIONED}
                req_sz_class = BaseAdminSerializer.get_crams_request_serializer_class()
                requestSerializer = req_sz_class(
                    instance=request_obj, data={id: request_obj.id}, partial=True, context=partial_request_context_obj)
                requestSerializer.is_valid(raise_exception=True)
                requestSerializer.save(project=request_obj.project)
            else:
                raise exceptions.ValidationError('cannot update request status without serializer context object')

    @classmethod
    def update_provisionable_item(cls, instance, validated_data, user_obj):
        pd = BaseProvisionUtils.build_new_provision_details(
            instance, validated_data, user_obj)
        pd.save()
        if instance.provision_details:
            old_pd = instance.provision_details
            old_pd.parent_provision_details = pd
            old_pd.updated_by = user_obj
            old_pd.save()
        instance.provision_details = pd
        instance.save()
        return instance
