from crams.permissions import IsCramsAuthenticated
from crams_storage.models import StorageProduct
from crams_storage.serializers.storage_product_serializers import ERBSystemStorageProductSerializer
from rest_framework import viewsets, decorators
from rest_framework.response import Response


class ERBStorageProductViewSet(viewsets.ViewSet):
    serializer_class = ERBSystemStorageProductSerializer
    # permission_classes = [IsCramsAuthenticated]
    queryset = StorageProduct.objects.none()

    @decorators.action(detail=False,
                       url_path='erb_storage_products/(?P<e_research_body>\w+)/(?P<e_research_system>\w+)')
    def storage_products(self, request, e_research_body, e_research_system):
        sp_list = []
        sp_qs = StorageProduct.objects.filter(
            e_research_system__name__iexact=e_research_system,
            e_research_system__e_research_body__name__iexact=e_research_body).order_by('id')
        if sp_qs:
            sp_list = self.serializer_class(sp_qs, manay=True).data
        return Response(sp_list)
