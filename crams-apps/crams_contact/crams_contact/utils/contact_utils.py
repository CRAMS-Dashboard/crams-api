# coding=utf-8
"""

"""

from crams.extension import config_init
from crams.utils import rest_utils
from crams import models as crams_models
from crams_contact import models as contact_models
from crams.utils.role import AbstractCramsRoleUtils


def system_identifiers(contact_obj):
    return contact_models.EResearchContactIdentifier.objects.filter(
        contact=contact_obj, parent_erb_contact_id__isnull=True)


def fetch_contact_for_user(user_obj):
    if isinstance(user_obj, crams_models.User):
        qs = contact_models.Contact.objects.filter(
            email__iexact=user_obj.email, latest_contact__isnull=True)
        if qs.exists():
            return qs.first()
    return None


def fetch_user_contact_if_exists(crams_user):
    return fetch_contact_for_user(crams_user)


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
    user_obj, _ = rest_utils.get_current_user_from_context(serializer_self)
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
    if isinstance(crams_user, crams_models.User):
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
                if erb not in config_init.ERB_PROVIDER_DISALLOW_LIST:
                    ret_set.add(erb_user_role)
                    continue

            for erbs in erb_user_role.admin_erb_systems.all():
                if erbs not in config_init.ERBS_PROVIDER_DISALLOW_LIST:
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
