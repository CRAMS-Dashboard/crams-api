# coding=utf-8
"""

"""
from crams_reports.serializers.storage_usage import ProjectSPUsageSerializer
from crams_allocation.viewsets.allocation_viewsets import ProjectRequestViewSet
from crams_reports.viewsets.reports import CramsReportViewSet

from crams_storage.models import StorageProduct


class ProjectStorageUsageViewset(ProjectRequestViewSet, CramsReportViewSet):
    serializer_class = ProjectSPUsageSerializer

    def get_request_param_storage_product_qs(self):
        if not self.e_research_system_param_qs:
            return StorageProduct.objects.all()

        return StorageProduct.objects.filter(
            e_research_system__in=self.e_research_system_param_qs)
