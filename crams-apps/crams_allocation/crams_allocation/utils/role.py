# coding=utf-8
"""

"""
from crams_contact.serializers.contact_erb_roles import ContactErbRoleSerializer
from crams_storage.models import StorageProduct
from crams_compute.models import ComputeProduct


class ProductRoleUtils(ContactErbRoleSerializer):
    @classmethod
    def get_provider_erbs_for_user(cls, user_obj):
        """
        return a list of erb systems serviced by the user_obj as a provider
        - The provider object in crams represents infrastructure provisioning team.
        - A single user can be associated with multiple infrastructure Products
        """
        provider_list = cls.get_authorised_provider_list(user_obj)
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
