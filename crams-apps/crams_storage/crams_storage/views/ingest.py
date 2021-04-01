# coding=utf-8
"""

"""
from rest_framework.decorators import api_view
from rest_framework.views import Response


@api_view(http_method_names=['GET'])
def recent_provision_id(request):
    """
        get recent_provision_id as list
        Dummy code: returns empty list
    :param request:
    :return:
    """
    return Response(list())
