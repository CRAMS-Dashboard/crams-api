# coding=utf-8
"""

"""
from crams.utils import django_utils
from crams.permissions import IsCramsAuthenticated
from crams_allocation.permissions import IsRequestApprover
from crams_allocation.product_allocation.models import Request
from crams_allocation.serializers import admin_serializers


class ApproveRequestViewSet(django_utils.CramsModelNoListViewSet):
    """
    class ApproveRequestViewSet
    """
    permission_classes = (IsCramsAuthenticated, IsRequestApprover)
    serializer_class = admin_serializers.ApproveRequestModelSerializer
    queryset = Request.objects.filter(
        current_request__isnull=True,
        request_status__code__in=admin_serializers.ADMIN_ENABLE_REQUEST_STATUS)
