from rest_framework.response import Response
from rest_framework.decorators import api_view
from crams_storage.models import StorageProduct
from crams_storage.serializers.storage_product_serializers import StorageProductSerializer

#  TODO: don't need it
# @api_view(http_method_names=['GET'])
# def fb_storage_product(request, fb_name):
#     """
#     list all storage products, <BR>
#      - filter by funding body name is provided as a parameter <BR>
#     usage: storage_products/<str:fb_name> <BR>
#     """
#     if not fb_name:
#         fb_name = 'NeCTAR'
#
#     nectar_sps = StorageProduct.objects.filter(
#         funding_body__name__iexact=fb_name.lower()).order_by('id')
#
#     sp_list = []
#     for sp in nectar_sps:
#         sp_list.append(StorageProductSerializer(sp).data)
#     return Response(sp_list)
