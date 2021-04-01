# coding=utf-8
"""

"""
from django.db.models import Q

from crams_allocation.models import RequestStatus
from crams_collection.utils import project_user_utils
from crams_allocation.product_allocation.models import StorageRequest


def get_user_storage_requests(
        user_obj, storage_product_qs=None, request_status_code=None):
    user_projects = project_user_utils.get_user_projects(user_obj)
    storage_request_qs = StorageRequest.objects.filter(
        request__project__in=user_projects)

    if storage_product_qs:
        storage_request_qs = storage_request_qs.filter(
            storage_product__in=storage_product_qs)

    if request_status_code:
        return storage_request_qs.filter(
            request__request_status__code=request_status_code)

    return storage_request_qs


def get_contact_storage_requests(
        contact_obj, storage_product_qs=None,
        request_status_code_list=None, ignore_status_code_for_current=False):
    ret_qs = StorageRequest.objects.none()

    qs_filter = Q()
    if storage_product_qs:
        if not storage_product_qs.exists():
            return ret_qs
        qs_filter = Q(storage_product__in=storage_product_qs)

    if request_status_code_list:
        request_status_qs = RequestStatus.objects.filter(
            code__in=request_status_code_list)
        if not request_status_qs.exists():
            return ret_qs
        status_filter = Q(request__request_status__in=request_status_qs)
        if ignore_status_code_for_current:
            status_filter = status_filter | Q(
                request__current_request__isnull=True)
        qs_filter = qs_filter & status_filter

    contact_projects = project_user_utils.get_contact_current_projects_qs(contact_obj)
    if not contact_projects.exists():
        return ret_qs

    project_filter = Q(request__project__in=contact_projects) | Q(
        request__project__current_project__in=contact_projects)

    qs_filter = qs_filter & project_filter
    storage_request_qs = StorageRequest.objects.filter(qs_filter)

    return storage_request_qs
