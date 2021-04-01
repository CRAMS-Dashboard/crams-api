# coding=utf-8
"""

"""

from crams.permissions import IsCramsAuthenticated
from crams.models import User
from crams.utils import viewset_utils
from crams_collection.utils import project_user_utils
from rest_framework import mixins


class ProvisionCommonViewSet(viewset_utils.LookupViewset,
                             mixins.UpdateModelMixin):
    permission_classes = [IsCramsAuthenticated]

    @classmethod
    def get_user_provision_erbs(cls, user_obj, e_research_body_obj=None):
        erb_set = set()
        if isinstance(user_obj, User):
            fn = project_user_utils.fetch_erb_userroles_with_provision_privileges
            user_erb_roles = fn(user_obj, e_research_body_obj)
            for erb_role in user_erb_roles:
                erb_set.add(erb_role.role_erb)
        return list(erb_set)

    @classmethod
    def provision_product_for_http_request(
            cls, http_request, product_data_list, serializer_class):

        sz_list = list()
        context = {'request': http_request}
        for pr_data in product_data_list:
            sz = serializer_class(data=pr_data, context=context)
            sz.is_valid()
            if sz.errors:
                pr_data['errors'] = sz.errors
            else:
                sz_list.append(sz)

        for sz in sz_list:
            sz.save()

        return product_data_list
