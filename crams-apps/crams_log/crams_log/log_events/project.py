# coding=utf-8
"""

"""

from crams_log.log_events import base
from crams_log import utils as crams_log_utils
from crams_log.constants import log_actions, log_types


LogUtils = crams_log_utils.LogUtils


# def log_project_metadata_change(before_json, after_json, user_obj, project, message, contact=None):
#     if not message:
#         message = 'Project data updated'
#     action = crams_log_utils.fetch_log_action(log_actions.UPDATE_FORM, 'Change Project metadata')
#     log_type = crams_log_utils.fetch_log_type(log_types.Project, 'Project')

#     log_obj =  base.CramsLogModelUtil.create_new_log(before_json, after_json, log_type, action, message, user_obj)

#     # link to relevant project log
#     LogUtils.link_project_log(log_obj, crams_project_id=project.id)
#     if contact:
#         LogUtils.link_contact_log(log_obj, contact.id)

#     return log_obj


# def log_allocation_metadata_change(before_json, after_json, user_obj, allocation_request, message, contact=None):
#     if not message:
#         message = 'Allocation data updated'
#     action = crams_log_utils.fetch_log_action(log_actions.UPDATE_FORM, 'Change Allocation metadata')
#     log_type = crams_log_utils.fetch_log_type(log_types.Allocation, 'Request')

#     log_obj =  base.CramsLogModelUtil.create_new_log(before_json, after_json, log_type, action, message, user_obj)

#     # link to relevant project log
#     project = allocation_request.project
#     LogUtils.link_allocation_log(log_obj, crams_request_db_id=allocation_request.id, crams_project_db_id=project.id)
#     if contact:
#         LogUtils.link_contact_log(log_obj, contact.id)

#     return log_obj


# def log_project_contact_update(before_json, after_json, user_obj, project, message, contact=None):
#     if not message:
#         message = 'New contact added to Project'
#     action = crams_log_utils.fetch_log_action(log_actions.UPDATE_FORM, 'Change Project Contact')
#     log_type = crams_log_utils.fetch_log_type(log_types.Project, 'Project')

#     log_obj = base.CramsLogModelUtil.create_new_log(before_json, after_json, log_type, action, message, user_obj)

#     # link to relevant project log
#     LogUtils.link_project_log(log_obj, crams_project_id=project.id)
#     if contact:
#         LogUtils.link_contact_log(log_obj, contact.id)

#     return log_obj
