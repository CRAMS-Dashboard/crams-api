# coding=utf-8
"""

"""
import logging

from crams.models import ProvisionDetails
from crams_provision.utils.base import BaseProvisionUtils
from crams.utils.role import AbstractCramsRoleUtils
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
    def update_request_status(cls, request_obj):
        if not request_obj.request_status.code == REQUEST_STATUS_APPROVED:
            msg = 'Cannot update status for non Approved Requests'
            raise exceptions.ValidationError(msg)
        valid_status = ProvisionDetails.PROVISIONED
        filter_qs = Q(provision_details__status=valid_status)

        sr_qs = request_obj.storage_requests.exclude(filter_qs)
        cr_qs = request_obj.compute_requests.exclude(filter_qs)
        if sr_qs.exists() or cr_qs.exists():
            # TODO check partial provision email send
            # notify_cls = allocation_notification.AllocationNotificationUtils
            # notify_cls.send_partial_provision_notification(
            #     request_obj, serializer_context)
            return

        # update request status to provisioned
        request_obj.request_status = \
            cls.get_request_status_obj_for_code(REQUEST_STATUS_PROVISIONED)
        request_obj.save()

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
        cls.update_request_status(instance.request)
        return instance
