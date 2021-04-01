# coding=utf-8
"""

"""

from django.db.models import Q
from rest_framework import exceptions
from crams import models
from crams.extension.config_init import ERB_PROVIDER_DISALLOW_LIST, ERBS_PROVIDER_DISALLOW_LIST
from crams.utils.role import AbstractCramsRoleUtils
from crams_collection.models import Project
from crams.models import ProductCommon
from crams_contact import models as contact_models
from crams_contact.utils import contact_utils
from crams_manager import models as manager_models


def fetch_user_contact_if_exists(crams_user):
    return contact_utils.fetch_contact_for_user(crams_user)


def get_current_user_from_context(serializer_self):
    current_user = None
    context = None

    if hasattr(serializer_self, 'context'):
        context = serializer_self.context
        current_user = context.get('current_user', None)
        if not current_user:
            http_request = serializer_self.context.get('request', None)
            if http_request:
                current_user = http_request.user
    elif serializer_self.request:
        current_user = serializer_self.request.user
        context = dict()
        context['request'] = serializer_self.request

    return current_user, context


def user_details_json(user_obj, null_default='System'):
    if user_obj:
        contact = fetch_user_contact_if_exists(user_obj)
        if contact:
            return {
                'email': contact.email,
                'first_name': contact.given_name,
                'last_name': contact.surname
            }
        return {
            'email': user_obj.email,
            'first_name': user_obj.first_name,
            'last_name': user_obj.last_name
        }
    return {
        'email': null_default,
        'first_name': null_default,
        'last_name': null_default
    }


def fetch_related_user_erb_system_list(serializer_self):
    user_obj, _ = get_current_user_from_context(serializer_self)
    if user_obj:
        return AbstractCramsRoleUtils.get_authorised_e_research_system_list(user_obj)
    return list()


def fetch_related_user_erb_list(serializer_self):
    ret_set = set()
    for erbs in fetch_related_user_erb_system_list(serializer_self):
        ret_set.add(erbs.e_research_body)
    return list(ret_set)


def fetch_erb_userroles_with_provision_privileges(
        crams_user, e_research_body_obj=None):
    """

    :param crams_user:
    :param e_research_body_obj:
    :return:
    """
    ret_set = set()
    if isinstance(crams_user, models.User):
        qs = contact_models.CramsERBUserRoles.objects.all()
        contact = fetch_user_contact_if_exists(crams_user)
        if contact:
            qs = qs.filter(contact=contact)
        if e_research_body_obj:
            qs = qs.filter(role_erb=e_research_body_obj)

        for erb_user_role in qs.all():
            erb = erb_user_role.role_erb
            if erb_user_role.providers.exists():
                ret_set.add(erb_user_role)
                continue

            if erb_user_role.is_erb_admin:
                if erb not in ERB_PROVIDER_DISALLOW_LIST:
                    ret_set.add(erb_user_role)
                    continue

            for erbs in erb_user_role.admin_erb_systems.all():
                if erbs not in ERBS_PROVIDER_DISALLOW_LIST:
                    ret_set.add(erb_user_role)
                    break

    return list(ret_set)


def fetch_contact_delegates_for_erb_systems(contact, erb_systems):
    erb_set = set()
    for erbs in erb_systems:
        erb_set.add(erbs.e_research_body)
    role_qs = contact.user_roles.filter(role_erb__in=erb_set,
                                        delegates__isnull=False)
    ret_set = set()
    if role_qs.exists():
        for erb_role in role_qs.all():
            ret_set = ret_set | set(erb_role.delegates.all())
    return list(ret_set)


def fetch_contact_organisation_qs(contact):
    org_pk_set = set()
    for org_manager in contact.manager_organisations.filter(active=True):
        org_pk_set.add(org_manager.organisation.id)
    return contact_models.Organisation.objects.filter(pk__in=org_pk_set)


def fetch_contact_faculties_qs(contact):
    faculty_pk_set = set()
    for erb_user_role in contact.manager_faculties.filter(active=True):
        faculty_pk_set.add(erb_user_role.faculty.id)

    org_qs = fetch_contact_organisation_qs(contact)

    qs_filter = Q(organisation__in=org_qs) | Q(pk__in=faculty_pk_set)
    return contact_models.Faculty.objects.filter(qs_filter)


def fetch_contact_departments_qs(contact):
    pk_set = set()
    qs_all = manager_models.DepartmentManager.objects
    for department_manager in qs_all.filter(active=True, contact=contact):
        pk_set.add(department_manager.department.id)

    faculty_qs = fetch_contact_faculties_qs(contact)

    qs_filter = Q(faculty__in=faculty_qs) | Q(pk__in=pk_set)
    return contact_models.Department.objects.filter(qs_filter)


def get_user_projects(user_obj):
    qs_filter = Q(project_contacts__contact__email__iexact=user_obj.email)
    return Project.objects.filter(qs_filter)


def get_contact_historical_projects_qs(contact_obj):
    # Do not use distinct here, instead use it in calling method
    qs = Project.objects.filter(
        project__project_contacts__contact=contact_obj)
    return qs


def get_contact_current_projects_qs(contact_obj):
    # Do not use distinct here, instead use it in calling method
    qs = get_contact_historical_projects_qs(contact_obj).filter(
        current_project__isnull=True)
    return qs


def is_contact_product_provider(contact, product):
    """
    return True is contact is a provider for the given product, else False
    :param contact:
    :param product:
    :return:
    """
    fn_msg = 'user_utils.is_contact_product_provider: '
    if not isinstance(contact, contact_models.Contact):
        raise exceptions.ValidationError(fn_msg + 'contact object required')
    if not isinstance(product, ProductCommon):
        raise exceptions.ValidationError(fn_msg + 'product object required')

    product_erb = product.e_research_system.e_research_body
    erb_role_qs = contact.user_roles.filter(role_erb=product_erb)
    if erb_role_qs.exists():
        erb_role = erb_role_qs.first()
        # Check if Provider role exists
        if product.provider and erb_role.providers.exists():
            if product.provider in erb_role.providers.all():
                return True

        # Check if erbAdmin and not in disallow Provider role list
        if product_erb not in ERB_PROVIDER_DISALLOW_LIST:
            if erb_role.is_erb_admin:
                return True

        # Check if erb System Admin and not in disallow Provider role list
        product_erbs = product.e_research_system
        if product_erbs not in ERBS_PROVIDER_DISALLOW_LIST:
            if product_erbs in erb_role.admin_erb_systems.all():
                return True
    return False


def is_project_visible_to_user(user_obj):
    contact = fetch_user_contact_if_exists(crams_user=user_obj)
    if not contact:
        return False


def fetch_project_contact_via_role(prj_contacts, role_str):
    contact_list = []
    for pc in prj_contacts:
        if pc.contact_role.name.lower() == role_str.lower():
            contact_list.append(pc.contact)

    return contact_list
