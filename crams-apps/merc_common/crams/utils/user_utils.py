# coding=utf-8
"""

"""
# from django.db.models import Q
# from rest_framework import exceptions
#
# from crams.config import config_init
# from crams import models
# from crams.utils.role import AbstractCramsRoleUtils as roleUtils
# from crams.manager import models as manager_models


# def fetch_user_contact_if_exists(crams_user):
#     return models.Contact.fetch_contact_for_user(crams_user)
#
# def user_details_json(user_obj, null_default='System'):
#     if user_obj:
#         contact = fetch_user_contact_if_exists(user_obj)
#         if contact:
#             return {
#                 'email': contact.email,
#                 'first_name': contact.given_name,
#                 'last_name': contact.surname
#             }
#         return {
#             'email': user_obj.email,
#             'first_name': user_obj.first_name,
#             'last_name': user_obj.last_name
#         }
#     return {
#         'email': null_default,
#         'first_name': null_default,
#         'last_name': null_default
#     }
#
#
# def fetch_related_user_erb_system_list(serializer_self):
#     user_obj, _ = get_current_user_from_context(serializer_self)
#     if user_obj:
#         return roleUtils.get_authorised_e_research_system_list(user_obj)
#     return list()
#
#
# def fetch_related_user_erb_list(serializer_self):
#     ret_set = set()
#     for erbs in fetch_related_user_erb_system_list(serializer_self):
#         ret_set.add(erbs.e_research_body)
#     return list(ret_set)
#
#
# def fetch_erb_userroles_with_provision_privileges(
#    # moved to crams_contact.utils.contact_utils
#
#
# def fetch_contact_delegates_for_erb_systems(contact, erb_systems):
#     erb_set = set()
#     for erbs in erb_systems:
#         erb_set.add(erbs.e_research_body)
#     role_qs = contact.user_roles.filter(role_erb__in=erb_set,
#                                         delegates__isnull=False)
#     ret_set = set()
#     if role_qs.exists():
#         for erb_role in role_qs.all():
#             ret_set = ret_set | set(erb_role.delegates.all())
#     return list(ret_set)
#
#
# def fetch_contact_organisation_qs(contact):
#     org_pk_set = set()
#     for org_manager in contact.manager_organisations.filter(active=True):
#         org_pk_set.add(org_manager.organisation.id)
#     return models.Organisation.objects.filter(pk__in=org_pk_set)
#
#
# def fetch_contact_faculties_qs(contact):
#     faculty_pk_set = set()
#     for erb_user_role in contact.manager_faculties.filter(active=True):
#         faculty_pk_set.add(erb_user_role.faculty.id)
#
#     org_qs = fetch_contact_organisation_qs(contact)
#
#     qs_filter = Q(organisation__in=org_qs) | Q(pk__in=faculty_pk_set)
#     return models.Faculty.objects.filter(qs_filter)


# def fetch_contact_departments_qs(contact):
#     pk_set = set()
#     qs_all = manager_models.DepartmentManager.objects
#     for department_manager in qs_all.filter(active=True, contact=contact):
#         pk_set.add(department_manager.department.id)
#
#     faculty_qs = fetch_contact_faculties_qs(contact)
#
#     qs_filter = Q(faculty__in=faculty_qs) | Q(pk__in=pk_set)
#     return models.Department.objects.filter(qs_filter)
#
#
# def get_user_projects(user_obj):
#     qs_filter = Q(project_contacts__contact__email__iexact=user_obj.email)
#     return models.Project.objects.filter(qs_filter)
#
#
# def get_user_storage_requests(
#         user_obj, storage_product_qs=None, request_status_code=None):
#     user_projects = get_user_projects(user_obj)
#     storage_request_qs = models.StorageRequest.objects.filter(
#         request__project__in=user_projects)
#
#     if storage_product_qs:
#         storage_request_qs = storage_request_qs.filter(
#             storage_product__in=storage_product_qs)
#
#     if request_status_code:
#         return storage_request_qs.filter(
#             request__request_status__code=request_status_code)
#
#     return storage_request_qs
#
#
# def get_contact_historical_projects_qs(contact_obj):
#     # Do not use distinct here, instead use it in calling method
#     qs = models.Project.objects.filter(
#         project__project_contacts__contact=contact_obj)
#     return qs
#
#
# def get_contact_current_projects_qs(contact_obj):
#     # Do not use distinct here, instead use it in calling method
#     qs = get_contact_historical_projects_qs(contact_obj).filter(
#         current_project__isnull=True)
#     return qs
#
#
# def get_contact_storage_requests(
#         contact_obj, storage_product_qs=None,
#         request_status_code_list=None, ignore_status_code_for_current=False):
#
#     ret_qs = models.StorageRequest.objects.none()
#
#     qs_filter = Q()
#     if storage_product_qs:
#         if not storage_product_qs.exists():
#             return ret_qs
#         qs_filter = Q(storage_product__in=storage_product_qs)
#
#     if request_status_code_list:
#         request_status_qs = models.RequestStatus.objects.filter(
#             code__in=request_status_code_list)
#         if not request_status_qs.exists():
#             return ret_qs
#         status_filter = Q(request__request_status__in=request_status_qs)
#         if ignore_status_code_for_current:
#             status_filter = status_filter | Q(
#                 request__current_request__isnull=True)
#         qs_filter = qs_filter & status_filter
#
#     contact_projects = get_contact_current_projects_qs(contact_obj)
#     if not contact_projects.exists():
#         return ret_qs
#
#     project_filter = Q(request__project__in=contact_projects) | Q(
#         request__project__current_project__in=contact_projects)
#
#     qs_filter = qs_filter & project_filter
#     storage_request_qs = models.StorageRequest.objects.filter(qs_filter)
#
#     return storage_request_qs
#
#
# def is_contact_product_provider(contact, product):
#     """
#     return True is contact is a provider for the given product, else False
#     :param contact:
#     :param product:
#     :return:
#     """
#     fn_msg = 'user_utils.is_contact_product_provider: '
#     if not isinstance(contact, models.Contact):
#         raise exceptions.ValidationError(fn_msg + 'contact object required')
#     if not isinstance(product, models.ProductCommon):
#         raise exceptions.ValidationError(fn_msg + 'product object required')
#
#     product_erb = product.e_research_system.e_research_body
#     erb_role_qs = contact.user_roles.filter(role_erb=product_erb)
#     if erb_role_qs.exists():
#         erb_role = erb_role_qs.first()
#         # Check if Provider role exists
#         if product.provider and erb_role.providers.exists():
#             if product.provider in erb_role.providers.all():
#                 return True
#
#         # Check if erbAdmin and not in disallow Provider role list
#         if product_erb not in config_init.ERB_PROVIDER_DISALLOW_LIST:
#             if erb_role.is_erb_admin:
#                 return True
#
#         # Check if erb System Admin and not in disallow Provider role list
#         product_erbs = product.e_research_system
#         if product_erbs not in config_init.ERBS_PROVIDER_DISALLOW_LIST:
#             if product_erbs in erb_role.admin_erb_systems.all():
#                 return True
#     return False
#
#
# def is_project_visible_to_user(user_obj):
#     contact = fetch_user_contact_if_exists(crams_user=user_obj)
#     if not contact:
#         return False
#
#
# def fetch_project_contact_via_role(prj_contacts, role_str):
#     contact_list = []
#     for pc in prj_contacts:
#         if pc.contact_role.name.lower() == role_str.lower():
#             contact_list.append(pc.contact)
#
#     return contact_list
