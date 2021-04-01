# coding=utf-8
"""

"""
from rest_framework.decorators import api_view
from rest_framework.views import Response

from crams_collection.models import GrantType


@api_view(http_method_names=['GET'])
def grant_types(request):
    """
        get Grant Type Objects as Dict
    :param request:
    :return:
    """
    grant_type_objs = GrantType.objects.all()

    grant_type_list = []
    for grant_type in grant_type_objs:
        grant_type_list.append({'id': grant_type.id,
                                'desc': grant_type.description})
    return Response(grant_type_list)
