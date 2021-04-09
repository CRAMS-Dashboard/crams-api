# coding=utf-8
"""

"""
from rest_framework import response, exceptions

from crams.permissions import IsCramsAuthenticated
from crams_reports.serializers.storage_usage import ProjectSPUsageSerializer
from crams_reports.serializers.storage_ingest_history import StorageProductProvisionIDSerializer

from crams_allocation.viewsets.allocation_viewsets import ProjectRequestViewSet
from crams_reports.viewsets.reports import CramsReportViewSet

from crams_storage.models import StorageProduct, StorageProductProvisionId


class ProjectStorageUsageViewset(ProjectRequestViewSet, CramsReportViewSet):
    serializer_class = ProjectSPUsageSerializer

    def get_request_param_storage_product_qs(self):
        if not self.e_research_system_param_qs:
            return StorageProduct.objects.all()

        return StorageProduct.objects.filter(
            e_research_system__in=self.e_research_system_param_qs)


class ProjectStorageUsageHistoryViewset(CramsReportViewSet):
    permission_classes = [IsCramsAuthenticated]
    serializer_class = StorageProductProvisionIDSerializer
    queryset = StorageProductProvisionId.objects.all()

    def get_queryset(self):
        super().setup_init_params()

        # get provision_id
        provision_id = self.request.query_params.get(
            'provision_id', None)
        storage_product_id = self.request.query_params.get(
            'storage_product_id', None)

        if not provision_id or not storage_product_id:
            raise exceptions.APIException(
                'No provision_id or storage product id provided')

        qs = self.queryset.filter(id=provision_id,
                                  storage_product_id=storage_product_id)
        return qs

    def list(self, request):
        # alters the response to return json object instead of list
        queryset = self.get_queryset()
        serializer = StorageProductProvisionIDSerializer(queryset, many=True)

        # returns an empty list if no data available
        data = []
        if serializer.data:
            data = serializer.data[0]

        return response.Response(data)
