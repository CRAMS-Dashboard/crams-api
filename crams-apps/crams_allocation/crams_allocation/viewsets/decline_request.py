# coding=utf-8
"""

"""
from crams.utils import django_utils
from crams.permissions import IsCramsAuthenticated
from crams_allocation.permissions import IsRequestApprover
from crams_allocation.product_allocation.models import Request
from crams_allocation.serializers import admin_serializers


class DeclineRequestViewSet(django_utils.CramsModelNoListViewSet):
    """
    class DeclineRequestViewSet
    """
    permission_classes = (IsCramsAuthenticated, IsRequestApprover)
    serializer_class = admin_serializers.DeclineRequestModelSerializer
    queryset = Request.objects.filter(
        current_request__isnull=True,
        request_status__code__in=admin_serializers.ADMIN_ENABLE_REQUEST_STATUS)
