# coding=utf-8
"""

"""
from json import dumps as json_dumps

from crams.models import CramsToken
from crams.utils import role

from crams_contact.models import CramsERBUserRoles
from crams_contact.utils import contact_utils

# Crams Role dict Keys
ADMIN_ROLE_KEY = 'admin'
APPROVER_ROLE_KEY = 'approver'
PROVIDER_ROLE_KEY = 'provisioner'
DELEGATE_ROLE_TYPE = 'delegate'
TENANT_MANAGER = 'tenant_manager'
SERVICE_MANAGEMENT_ROLE_TYPE = 'service_management'
FACULTY_MANAGEMENT_ROLE_TYPE = 'faculty_management'
LEGACY_ROLES_KEY = 'global'


class ContactErbRoleSerializer(role.AbstractCramsRoleUtils):
    @classmethod
    def setup_crams_token_and_roles(cls, user_obj):
        crams_token, created = CramsToken.objects.get_or_create(user=user_obj)
        if crams_token.is_expired():  # Expire existing Token
            crams_token.delete()
            crams_token = CramsToken(user=user_obj)

        crams_token.ks_roles = json_dumps(cls.build_user_roles(user_obj))
        crams_token.save()
        return crams_token

    @classmethod
    def build_user_roles(cls, user_obj):
        contact = contact_utils.fetch_contact_for_user(user_obj)
        if not contact:
            return dict()
        return cls.build_contact_roles(contact)

    @classmethod
    def build_contact_roles(cls, contact):
        def update_roles_for_erb_system(erb_system_obj):
            approver_set.add(erb_system_obj.approver_role)
            if hasattr(erb_system_obj, 'storageproduct'):
                for sp in erb_system_obj.storageproduct.all():
                    provider_set.add(sp.provider.provider_role)
            if hasattr(erb_system_obj, 'computeproduct'):
                for cp in erb_system_obj.computeproduct.all():
                    provider_set.add(cp.provider.provider_role)

        roles_dict = dict()
        if not contact:
            return roles_dict

        admin_set = set()
        approver_set = set()
        provider_set = set()

        current_erb_roles = CramsERBUserRoles.query_current_roles(contact)
        if current_erb_roles.exists():
            for erb_user_role in current_erb_roles.filter(
                    end_date_ts__isnull=True):
                if erb_user_role.is_erb_admin:
                    admin_set.add(erb_user_role.role_erb.admin_role)
                    for erb_system in erb_user_role.role_erb.systems.all():
                        update_roles_for_erb_system(erb_system)

                if erb_user_role.admin_erb_systems.exists():
                    for erb_system in erb_user_role.admin_erb_systems.all():
                        admin_set.add(erb_system.admin_role)
                        update_roles_for_erb_system(erb_system)

                if erb_user_role.approver_erb_systems.exists():
                    for erb_system in erb_user_role.approver_erb_systems.all():
                        approver_set.add(erb_system.approver_role)

                if erb_user_role.delegates.exists():
                    for delegate in erb_user_role.delegates.all():
                        approver_set.add(delegate.approver_role)

                if erb_user_role.providers.exists():
                    for provider in erb_user_role.providers.all():
                        provider_set.add(provider.provider_role)

        if admin_set:
            roles_dict[ADMIN_ROLE_KEY] = list(admin_set)
        if approver_set:
            roles_dict[APPROVER_ROLE_KEY] = list(approver_set)
        if provider_set:
            roles_dict[PROVIDER_ROLE_KEY] = list(provider_set)

        if hasattr(contact, 'servicemanager') and contact.servicemanager.active:
            roles_dict[SERVICE_MANAGEMENT_ROLE_TYPE] = [
                contact.servicemanager.manager_role]

        manager_roles = set()
        if hasattr(contact, 'manager_faculties'):
            for faculty_manager in contact.manager_faculties.filter(active=True):
                manager_roles.add(faculty_manager.faculty.manager_role)
        if hasattr(contact, 'manager_organisations'):
            for org_manager in contact.manager_organisations.filter(active=True):
                for faculty in org_manager.organisation.faculties.all():
                    manager_roles.add(faculty.manager_role)
        if manager_roles:
            roles_dict[FACULTY_MANAGEMENT_ROLE_TYPE] = list(manager_roles)

        return roles_dict
