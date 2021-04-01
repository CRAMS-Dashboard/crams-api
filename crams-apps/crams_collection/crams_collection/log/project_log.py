# coding=utf-8
"""

"""
from crams_log.log_events import base
from crams_log.utils import lookup_utils
from crams_log.constants import log_actions, log_types
from crams_collection.models import ProjectLog
from crams_contact.models import ContactLog
from crams_collection.serializers import base_project_serializer


class ProjectMetaLogger:
    @classmethod
    def setup_project_log(cls, before_json, after_json, user_obj, project, message, contact=None):
        if not message:
            message = 'Project data updated'
        action = lookup_utils.fetch_log_action(log_actions.UPDATE_FORM, 'Change Project metadata')
        log_type = lookup_utils.fetch_log_type(log_types.Project, 'Project')

        log_obj = base.CramsLogModelUtil.create_new_log(before_json, after_json, log_type, action, message, user_obj)

        # link to relevant project log
        ProjectLog.link_log(log_obj, project_obj=project)
        if contact:
            ContactLog.link_log(log_obj, crams_contact_obj=contact)

        return log_obj

    @classmethod
    def build_json(cls, project_obj, context):
        if project_obj:
            sz = base_project_serializer.ReadOnlyProjectSerializer(project_obj, context=context)
            return sz.data

    @classmethod
    def log_project_metadata_change(
            cls, project_obj, existing_project_obj, created_by_user_obj, message, contact, sz_context):
        before_json = cls.build_json(existing_project_obj, context=sz_context)
        after_json = cls.build_json(project_obj, context=sz_context)
        return cls.setup_project_log(
            before_json, after_json, created_by_user_obj, project_obj, message, contact)
