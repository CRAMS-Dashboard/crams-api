# coding=utf-8
"""

"""

from crams.utils import role
from crams_contact import models as contact_models
from crams_allocation.allocation.storage import StorageProduct
from crams_allocation.allocation.compute import ComputeProduct
from crams_contact.models import CramsERBUserRoles


class CramsRoleUtils(role.AbstractCramsRoleUtils):
    @classmethod
    def build_user_roles(cls, user_obj):
        contact = contact_models.Contact.fetch_contact_for_user(user_obj)
        if not contact:
            return dict()
        return build_contact_roles(contact)

    @classmethod
    def build_contact_roles(cls, contact):
        def update_roles_for_erb_system(erb_system_obj):
            approver_set.add(erb_system_obj.approver_role)
            for sp in erb_system_obj.storageproduct.all():
                provider_set.add(sp.provider.provider_role)
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
        if contact.manager_faculties.exists():
            for faculty_manager in contact.manager_faculties.filter(active=True):
                manager_roles.add(faculty_manager.faculty.manager_role)
        if contact.manager_organisations.exists():
            for org_manager in contact.manager_organisations.filter(active=True):
                for faculty in org_manager.organisation.faculties.all():
                    manager_roles.add(faculty.manager_role)
        if manager_roles:
            roles_dict[FACULTY_MANAGEMENT_ROLE_TYPE] = list(manager_roles)

        return roles_dict

    def get_provider_erbs_for_user(self, user):
        provider_list = self.get_authorised_provider_list(user)
        ret_set = set()
        if not provider_list:
            return list()

        product_qs = ComputeProduct.objects.filter(provider__in=provider_list)
        for compute_product in product_qs:
            ret_set.add(compute_product.e_research_system)

        product_qs = StorageProduct.objects.filter(provider__in=provider_list)
        for storage_product in product_qs:
            ret_set.add(storage_product.e_research_system)

        return list(ret_set)
