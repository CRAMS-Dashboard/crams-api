# coding=utf-8
"""

"""
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@csrf_exempt
def rapid_connect_auth_view(request):
    ret_dict = dict()
    for key, value in request.POST.items():
        ret_dict[key] = value
    return JsonResponse(ret_dict)
