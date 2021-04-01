# coding=utf-8
"""

"""
from crams.permissions import IsCramsAuthenticated
from rest_framework.views import APIView

from crams_allocation.constants import api

from crams_allocation.views.project_request_list import BaseRequestList


class ProvisionRequestListView(APIView, BaseRequestList):
    permission_classes = [IsCramsAuthenticated]

    # noinspection PyUnusedLocal
    def get(self, http_request, format=None):
        return self.build_project_request_list_for_request_status(http_request, req_status=api.REQ_APPROVED)
