# coding=utf-8
"""

"""
from rest_framework.response import Response
from rest_framework import viewsets

from crams.permissions import IsCramsAuthenticated
from crams.models import EResearchBodySystem
from crams.utils.role import AbstractCramsRoleUtils


class PrevUserFundingBodyRoleList(viewsets.ViewSet):
    """
     current user approver role list
    """
    permission_classes = [IsCramsAuthenticated]

    # noinspection PyMethodMayBeStatic
    def list(self, request):
        """
            List
        :param request:
        :return:
        """
        # ret_list = self.fetch_user_funding_body_roles(request.user)
        ret_list = self.fetch_user_system_roles(request.user)
        return Response(ret_list)

    @classmethod
    def fetch_user_system_roles(cls, user_obj):
        ret_list = []
        system_list = AbstractCramsRoleUtils.get_authorised_e_research_system_list(user_obj)
        if len(system_list) > 0:
            for es in EResearchBodySystem.objects.filter(name__in=system_list):
                current_dict = {'id': es.id, 'name': es.name}
                ret_list.append(current_dict)
                current_dict[AbstractCramsRoleUtils.APPROVER_ROLE_KEY] = True
        return ret_list
