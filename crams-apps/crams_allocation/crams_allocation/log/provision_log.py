# coding=utf-8
"""

"""
import copy

from crams_collection.utils import project_user_utils
from crams_contact.models import ContactLog
from crams_log.constants import log_actions, log_types
from crams_log.log_events import base
from crams_log.utils import lookup_utils

from crams_allocation.models import AllocationLog


class ProvisionMetaLogger:
    @classmethod
    def log_provision_id_change(cls, product_request_instance, old_provision_id, user_obj, message=None):
        request = product_request_instance.request
        common_json = dict()
        common_json['id'] = product_request_instance.id
        common_json['storage_product'] = {
            'id': product_request_instance.storage_product.id,
            'name': product_request_instance.storage_product.name
        }
        common_json['request'] = {
            'id': request.id,
            'e_research_system': {
                'name': request.e_research_system.name,
                'e_research_body': request.e_research_system.e_research_body.name
            },
            'project': product_request_instance.request.project.title
        }
        before_json = copy.copy(common_json)
        if old_provision_id:
            before_json['provision_id'] = {
                'id': old_provision_id.id,
                'provision_id': old_provision_id.provision_id
            }

        after_json = copy.copy(common_json)
        provision_id = product_request_instance.provision_id
        if provision_id:
            after_json['provision_id'] = {
                'id': provision_id.id,
                'provision_id': provision_id.provision_id
            }

        if not message:
            sp = product_request_instance.storage_product.name
            old_pid = None
            if old_provision_id:
                old_pid = old_provision_id.provision_id
            new_pid = None
            if provision_id:
                new_pid = provision_id.provision_id
            message = 'Provision Id for {} changed from {} to {}'.format(sp, old_pid, new_pid)

        log_obj = cls.build_provision_metadata_change_json(
            before_json=before_json, after_json=after_json, user_obj=user_obj, crams_request=request, message=message)

        return log_obj

    @classmethod
    def build_provision_metadata_change_json(cls, before_json, after_json, user_obj, crams_request, message):
        contact = project_user_utils.fetch_user_contact_if_exists(user_obj)
        log_obj = cls.log_provision_metadata_change(
            before_json=before_json, after_json=after_json, user_obj=user_obj,
            crams_request=crams_request, message=message, contact=contact)
        return log_obj

    @classmethod
    def log_provision_metadata_change(cls, before_json, after_json, user_obj, crams_request, message=None, contact=None):
        if not message:
            message = 'Provision id changed'
        action = lookup_utils.fetch_log_action(log_actions.PROVISION, 'Change Provision Id')
        log_type = lookup_utils.fetch_log_type(log_types.Allocation, 'Storage Request')

        log_obj = base.CramsLogModelUtil.create_new_log(before_json, after_json, log_type, action, message, user_obj)

        # link log to relevant Project, Allocation and Contact
        AllocationLog.link_log(log_obj, request_obj=crams_request)
        if contact:
            ContactLog.link_log(log_obj, crams_contact_obj=contact)

        return log_obj
