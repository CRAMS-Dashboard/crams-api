# #
# """
# Crams Logging utils
# """
# from crams_log.log_events import project as project_logger
#
# from crams_log import utils as crams_log_utils
#
# from crams_log.log_events import login as crams_log_login
# from crams_log.log_events import provision as crams_log_provision
# from crams.utils import user_utils
#
# LogUtils = crams_log_utils.LogUtils
#
#
# def log_user_login(http_request, user_obj, msg):
#     contact = user_utils.fetch_user_contact_if_exists(user_obj)
#     return crams_log_login.log_user_login(http_request, user_obj, message=msg, contact=contact)
#
#
# def log_redirect_user_login(http_request, user_obj, msg, override_referer=None):
#     contact = user_utils.fetch_user_contact_if_exists(user_obj)
#     return crams_log_login.log_user_login(
#         http_request, user_obj, message=msg, contact=contact, override_referer=override_referer)
#
#
# def log_change_provision_id(before_json, after_json, user_obj, crams_request, message):
#     contact = user_utils.fetch_user_contact_if_exists(user_obj)
#     log_obj = crams_log_provision.change_provision_id(
#         before_json=before_json, after_json=after_json, user_obj=user_obj,
#         crams_request=crams_request, message=message, contact=contact)
#     return log_obj
#
#
# def log_project_metadata_change(before_json, after_json, user_obj, project, message, contact=None):
#     return project_logger.log_project_metadata_change(
#         before_json, after_json, user_obj, project, message, contact)


def generate_before_after_json(existing_instance, validated_data, check_field_extract_fn_dict):
    """
    For related fields, validated_data must contain related object instead of json,
        - otherwise this function will not identify changed fields correctly
    :param existing_instance:
    :param validated_data:
    :param check_field_extract_fn_dict:
        This dict should map related fields to a function
            - that can handle both related objects and regular json data input by user
    :return: changed_fields, before_json, after_json
    """
    changed_fields_set = set()
    before_json = dict()
    after_json = dict()
    for field, json_fn in check_field_extract_fn_dict.items():
        new_field_val = validated_data.get(field)
        if json_fn:
            new_field_val = json_fn(new_field_val)
        after_json[field] = new_field_val

        old_field_val = None
        if existing_instance:
            old_field_val = getattr(existing_instance, field)
            if json_fn:
                old_field_val = json_fn(old_field_val)
            before_json[field] = old_field_val

        if not old_field_val == new_field_val:
            changed_fields_set.add(field)

    return changed_fields_set, before_json, after_json


# class ProjectMetaLogger:
#     @classmethod
#     def build_json(cls, project_obj, context):
#         if project_obj:
#             data = {}  # TODO delete this dummy statement
#             print(context)  # TODO delete this dummy statement
#             # TODO data = base_project_serializer.ReadOnlyProjectSerializer(project_obj, context=context).data
#             # TODO data.pop('requests', None)
#             return data
#
#     @classmethod
#     def log_project_metadata_change(
#             cls, project_obj, existing_project_obj, created_by_user_obj, message, contact, sz_context):
#         before_json = cls.build_json(existing_project_obj, context=sz_context)
#         after_json = cls.build_json(project_obj, context=sz_context)
#         return project_logger.log_project_metadata_change(
#             before_json, after_json, created_by_user_obj, project_obj, message, contact)
#
#
# class RequestMetaLogger:
#     @classmethod
#     def build_json(cls, request_obj, context):
#         if request_obj:
#             data = requestSerializers.ReadOnlyCramsRequestSerializer(request_obj, context=context).data
#             return data
#
#     @classmethod
#     def log_allocation_metadata_change(
#             cls, request_obj, existing_request_obj, created_by_user_obj, message, contact, sz_context):
#         before_json = cls.build_json(existing_request_obj, context=sz_context)
#         after_json = cls.build_json(request_obj, context=sz_context)
#         return project_logger.log_allocation_metadata_change(
#             before_json, after_json, created_by_user_obj, request_obj, message, contact)
#
#
# class ProjectContactLogger:
#     @classmethod
#     def build_json(cls, project, contact, contact_role):
#         ret_dict = dict()
#         if project:
#             ret_dict['project'] = {
#                 'id': project.id,
#                 'title': project.title
#             }
#         if contact:
#             ret_dict['contact'] = {
#                 'id': contact.id,
#                 'email': contact.email
#             }
#         if contact_role:
#             ret_dict['role'] = {
#                 'name': contact_role.name,
#                 'e_research_body': contact_role.e_research_body.name
#             }
#         return ret_dict
#
#     @classmethod
#     def log_project_contact_add(cls, project, contact, contact_role, created_by_user_obj):
#         before_json = None
#         after_json = cls.build_json(project, contact, contact_role)
#         message = '{} added to project role {}'.format(contact.email, contact_role.name)
#         return project_logger.log_project_contact_update(
#             before_json, after_json, created_by_user_obj, project, message, contact)
#
#     @classmethod
#     def log_remove_project_contact(cls, project, contact, contact_role, created_by_user_obj):
#         before_json = None
#         after_json = cls.build_json(project, contact, contact_role)
#         message = 'removed role {} for {}'.format(contact_role.name, contact.email)
#         return project_logger.log_project_contact_update(
#             before_json, after_json, created_by_user_obj, project, message, contact)
