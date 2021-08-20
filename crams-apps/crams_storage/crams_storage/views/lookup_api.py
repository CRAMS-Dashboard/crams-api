from crams.permissions import IsCramsAuthenticated
from crams_storage.models import StorageProduct
from crams_storage.serializers.storage_product_serializers import ERBSystemStorageProductSerializer
from rest_framework import viewsets, decorators
from rest_framework.response import Response
from crams.models import EResearchBodySystem

class ERBStorageProductViewSet(viewsets.ViewSet):
    serializer_class = ERBSystemStorageProductSerializer
    # permission_classes = [IsCramsAuthenticated]
    queryset = StorageProduct.objects.none()

    @decorators.action(detail=False,
                       url_path='storage_products/(?P<e_research_body>[-\w]+)/(?P<e_research_system>[-\w]+)')
    def storage_products(self, request, e_research_body, e_research_system):
        sp_list = []
        try:
            e_research_system_obj = EResearchBodySystem.objects.get(name__iexact=e_research_system,
                                                                    e_research_body__name__iexact=e_research_body)
            sp_qs = StorageProduct.objects.filter(e_research_system=e_research_system_obj).order_by('id')
            if sp_qs:
                sp_list = self.serializer_class(sp_qs, many=True).data
        except Exception as ex:
            print('--- storage_product api exception: {}'.format(ex))
            pass
        return Response(sp_list)
