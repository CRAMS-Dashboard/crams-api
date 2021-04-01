# # coding=utf-8
# """
#     Validate Config
# """
# from rest_framework import exceptions
# from crams.config import config_init
# from crams.common import project_id_generators
# from crams import models
#
#
# Project ErbId related dict
#     key: (id_key_name, erb_name)
#     value: (generator_fn, validate_fn)
ERBS_PROJECT_ID_UPDATE_FN_MAP = dict()

# Applicant Default role, per system
SYSTEM_APPLICANT_DEFAULT_ROLE = dict()

# def get_erb_id_obj(er_body_name, key):
#     try:
#         erb_id_obj = models.EResearchBodyIDKey.objects.get(
#             key=key, e_research_body__name=er_body_name)
#         return erb_id_obj
#     except models.EResearchBodyIDKey.DoesNotExist:
#         msg = 'ERB Id not found {}/{}'.format(key, er_body_name)
#         raise exceptions.ValidationError(msg)
#
# #
# # def build_create_role_for_key(erb_id_obj, project_obj, contact):
# #     pc_contact_filter = project_obj.project_contacts.filter(
# #         contact=contact, contact_role__read_only=False)
# #     if pc_contact_filter.exists():
# #         return models.CramsERBUserRoles(
# #             contact=contact, role_erb=erb_id_obj.e_research_body)
#
#
# def update_erb_project_ids_for_key(request_obj, user_erb_roles, contact):
#     if not user_erb_roles:
#         user_erb_roles = list()
#
#     project = request_obj.project
#     curr_erb = request_obj.e_research_system.e_research_body
#     role_erb_set = set()
#     for role in user_erb_roles:
#         role_erb_set.add(role.role_erb)
#
#     for (id_key_name, erb_name), (gen_fn, validate_fn) in \
#             config_init.ERBS_PROJECT_ID_UPDATE_FN_MAP.items():
#         # Create project ids relevant to request e_research_body only.
#         if not erb_name == curr_erb.name:
#             continue
#
#         erb_id_obj = get_erb_id_obj(erb_name, id_key_name)
#         new_identifier = None
#         if gen_fn:
#             new_identifier = gen_fn(project, erb_id_obj, validate_fn)
#         if new_identifier:
#             system = {
#                 'e_research_body': erb_name,
#                 'key': id_key_name
#             }
#             if erb_name not in role_erb_set:
#                 user_erb_roles.append(
#                     build_create_role_for_key(erb_id_obj, project, contact))
#                 role_erb_set.add(erb_name)
#
#             project_id_generators.save_erb_project_id(
#                 project, system, new_identifier, user_erb_roles)
#
#
# def update_erb_request_ids_for_key(request_obj, user_erb_roles, contact):
#     pass  # TBD
