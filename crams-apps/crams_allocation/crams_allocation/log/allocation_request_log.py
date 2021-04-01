# coding=utf-8
"""

"""
from crams_allocation.serializers.base import ReadOnlyCramsRequestWithoutProjectSerializer
from crams_log.log_events import base
from crams_log.utils import lookup_utils
from crams_log.constants import log_actions, log_types
from crams_contact.models import ContactLog
from crams_allocation.models import AllocationLog


class RequestMetaLogger:
    @classmethod
    def build_json(cls, request_obj, context):
        if request_obj:
            data = ReadOnlyCramsRequestWithoutProjectSerializer(request_obj, context=context).data
            return data

    @classmethod
    def build_allocation_metadata_change_json(
            cls, request_obj, existing_request_obj, created_by_user_obj, message, contact, sz_context):
        before_json = cls.build_json(existing_request_obj, context=sz_context)
        after_json = cls.build_json(request_obj, context=sz_context)
        return cls.log_allocation_metadata_change(
            before_json, after_json, created_by_user_obj, request_obj, message, contact)

    @classmethod
    def log_allocation_metadata_change(
            cls, before_json, after_json, user_obj, allocation_request, message, contact=None):
        if not message:
            message = 'Allocation data updated'
        action = lookup_utils.fetch_log_action(log_actions.UPDATE_FORM, 'Change Allocation metadata')
        log_type = lookup_utils.fetch_log_type(log_types.Allocation, 'Request')

        log_obj = base.CramsLogModelUtil.create_new_log(before_json, after_json, log_type, action, message, user_obj)

        # link to relevant allocation and contact log
        AllocationLog.link_log(log_obj, request_obj=allocation_request)
        if contact:
            ContactLog.link_log(log_obj, contact)

        return log_obj