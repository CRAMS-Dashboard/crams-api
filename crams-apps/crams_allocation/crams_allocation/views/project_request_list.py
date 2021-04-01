# from d3_prod - crams-apps.crams.api.v1.projectRequestListAPI
# coding=utf-8
"""
 project request lost APIs
"""
from crams.permissions import IsCramsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from crams_allocation.constants import api
from crams_allocation.utils import project_request_list_utils


class EResearchAllocationsCounter(APIView):
    """
        FundingBodyAllocationsCounter
    """
    permission_classes = [IsCramsAuthenticated]

    # noinspection PyUnusedLocal
    def get(self, request, format=None):
        ret_dict = {}
        user_systems = project_request_list_utils.get_e_research_systems_for_request_user(request)

        print('user systems', user_systems)
        if user_systems:
            return Response(project_request_list_utils.get_request_status_count(user_systems))

        return Response(ret_dict)


class BaseRequestList:
    @classmethod
    def build_project_request_list_for_request_status(cls, http_request, req_status=api.REQ_NEW):
        ret_dict = {}
        user_er_systems = project_request_list_utils.get_e_research_systems_for_request_user(http_request)

        if user_er_systems or req_status == api.REQ_ACTIVE:
            projects_dict = project_request_list_utils.query_projects(
                http_request, user_er_systems, req_status)
            return project_request_list_utils.populate_project_list_response(
                http_request, projects_dict, True)

        return Response(ret_dict)
