# # coding=utf-8
# """
#
# """
#
# from crams_log.log_events import base
# from crams_log.constants import log_actions, log_types
# from crams_log.utils import lookup_utils
#
#
# def change_provision_id(before_json, after_json, user_obj, crams_request, message=None, contact=None):
#     if not message:
#         message = 'Provision id changed'
#     action = lookup_utils.fetch_log_action(log_actions.PROVISION, 'Change Provision Id')
#     log_type = lookup_utils.fetch_log_type(log_types.Allocation, 'Storage Request')
#
#     log_obj = base.CramsLogModelUtil.create_new_log(before_json, after_json, log_type, action, message, user_obj)
#
#     # link log to relevant Project, Allocation and Contact
#     LogUtils.link_allocation_log(
#         log_obj, crams_request_db_id=crams_request.id, crams_project_db_id=crams_request.project.id)
#     if contact:
#         LogUtils.link_contact_log(log_obj, crams_contact_db_id=contact.id)
#
#     return log_obj
