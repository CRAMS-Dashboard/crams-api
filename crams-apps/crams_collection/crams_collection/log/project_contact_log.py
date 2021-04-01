# coding=utf-8
"""

"""
from crams_log.log_events import base
from crams_log.utils import lookup_utils
from crams_log.constants import log_actions, log_types
from crams_collection.models import ProjectLog
from crams_contact.models import ContactLog


class ProjectContactLogger:
    @classmethod
    def build_json(cls, project, contact, contact_role):
        ret_dict = dict()
        if project:
            ret_dict['project'] = {
                'id': project.id,
                'title': project.title
            }
        if contact:
            ret_dict['contact'] = {
                'id': contact.id,
                'email': contact.email
            }
        if contact_role:
            ret_dict['role'] = {
                'name': contact_role.name,
                'e_research_body': contact_role.e_research_body.name
            }
        return ret_dict

    @classmethod
    def log_project_contact_update(cls, before_json, after_json, user_obj, project, message, contact=None):
        if not message:
            message = 'New contact added to Project'
        action = lookup_utils.fetch_log_action(log_actions.UPDATE_FORM, 'Change Project Contact')
        log_type = lookup_utils.fetch_log_type(log_types.Project, 'Project')

        log_obj = base.CramsLogModelUtil.create_new_log(before_json, after_json, log_type, action, message, user_obj)

        # link to relevant project log
        ProjectLog.link_log(log_obj, project_obj=project)
        if contact:
            ContactLog.link_log(log_obj, crams_contact_obj=contact)

        return log_obj

    @classmethod
    def log_project_contact_add(cls, project, contact, contact_role, created_by_user_obj):
        before_json = None
        after_json = cls.build_json(project, contact, contact_role)
        message = '{} added to project role {}'.format(contact.email, contact_role.name)
        return cls.log_project_contact_update(
            before_json, after_json, created_by_user_obj, project, message, contact)

    @classmethod
    def log_remove_project_contact(cls, project, contact, contact_role, created_by_user_obj):
        before_json = None
        after_json = cls.build_json(project, contact, contact_role)
        message = 'removed role {} for {}'.format(contact_role.name, contact.email)
        return cls.log_project_contact_update(
            before_json, after_json, created_by_user_obj, project, message, contact)
