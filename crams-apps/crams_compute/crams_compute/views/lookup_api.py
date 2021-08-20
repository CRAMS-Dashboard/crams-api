from crams.permissions import IsCramsAuthenticated
from crams_compute import models
from crams_compute.serializers.compute_product import ERBSystemComputeProductSerializer
from rest_framework import viewsets, decorators
from rest_framework.response import Response


class ERBComputeProductViewSet(viewsets.ViewSet):
    serializer_class = ERBSystemComputeProductSerializer
    # permission_classes = [IsCramsAuthenticated]
    queryset = models.ComputeProduct.objects.none()

    @decorators.action(detail=False,
                       url_path='compute_products/(?P<e_research_body>\w+)/(?P<e_research_system>\w+)')
    def compute_products(self, request, e_research_body, e_research_system):
        cp_list = []
        comp_prod_qs = models.ComputeProduct.objects.filter(
            e_research_system__e_research_body__name__iexact=e_research_body,
            e_research_system__name__iexact=e_research_system).order_by('id')
        if comp_prod_qs:
            cp_list = self.serializer_class(comp_prod_qs, many=True).data

        return Response(cp_list)
