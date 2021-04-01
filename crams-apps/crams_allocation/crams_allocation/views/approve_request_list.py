# coding=utf-8
"""

"""
from crams.permissions import IsCramsAuthenticated
from rest_framework.views import APIView

from crams_allocation.constants import api

from crams_allocation.views.project_request_list import BaseRequestList


class ApproveRequestListView(APIView, BaseRequestList):
    permission_classes = [IsCramsAuthenticated]

    # noinspection PyUnusedLocal
    def get(self, http_request, format=None):
        req_status = http_request.query_params.get('req_status', api.REQ_NEW)
        return self.build_project_request_list_for_request_status(http_request, req_status=req_status)
