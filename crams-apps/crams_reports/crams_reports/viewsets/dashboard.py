# coding=utf-8
"""
Dashboard View definitions
"""
from crams import permissions
from crams_collection.models import Project

from crams_reports.serializers import dashboard_serializers
from crams_allocation.viewsets.list_request import AllocationListViewset


class DashboardViewset(AllocationListViewset):
    """
    class DashboardViewset
    """
    permission_classes = [permissions.IsCramsAuthenticated]
    queryset = Project.objects.none()
    serializer_class = dashboard_serializers.DashboardProjectListSerializer

    @classmethod
    def get_list_serializer_class(cls):
        return cls.serializer_class
