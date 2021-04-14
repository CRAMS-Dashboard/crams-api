# # coding=utf-8
# """
#
# """

from crams.permissions import IsCramsAuthenticated, IsActiveProvider
from crams.utils import django_utils
from crams.utils.role import AbstractCramsRoleUtils
from crams_allocation.product_allocation.models import Request
from crams_collection.models import Project
from crams_collection.utils import project_user_utils
from django.db.models import Q
from rest_framework import exceptions as rest_exceptions
from rest_framework import response, viewsets

from crams_provision.serializers.manual_provision import provision_serializers
from crams_provision.serializers.product_provision import PROVISION_ENABLE_REQUEST_STATUS


# class UpdateProvisionProjectViewSet(django_utils.CramsModelViewSet):
#     """
#     class UpdateProvisionProjectViewSet
#     """
#     permission_classes = (IsCramsAuthenticated, IsActiveProvider)
#     serializer_class = provision_serializers.UpdateProvisionProjectSerializer
#     queryset = Project.objects.filter(
#         current_project__isnull=True,
#         requests__current_request__isnull=True,
#         requests__request_status__code__in=PROVISION_ENABLE_REQUEST_STATUS)
#
#     # noinspection PyProtectedMember
#     def list(self, request, **kwargs):
#         """
#
#         :param request:
#         :param kwargs:
#         :return:
#         """
#         return response.Response([])


class AbstractListProvisionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsCramsAuthenticated,
                          IsActiveProvider)

    def filter_queryset(self, queryset):  # for List
        """
        filter_queryset
        :param queryset:
        :return: :raise NotFound:
        """
        return self.filter_provision_view_queryset(queryset)

    def filter_provision_view_queryset(self, queryset):
        current_user, _ = project_user_utils.get_current_user_from_context(self)
        if not AbstractCramsRoleUtils.is_user_a_provider(current_user):
            msg = 'User does not have a provider Role'
            raise rest_exceptions.NotFound(msg)

        crams_user = self.request.user
        valid_providers = AbstractCramsRoleUtils.get_authorised_provider_list(crams_user)
        if not valid_providers:
            msg = 'User {} does not have an active provider Role'
            raise rest_exceptions.NotFound(msg.format(repr(crams_user)))
        vp = valid_providers

        project_filter = \
            Q(requests__compute_requests__compute_product__provider__in=vp) | \
            Q(requests__storage_requests__storage_product__provider__in=vp)
        request_filter = \
            Q(compute_requests__compute_product__provider__in=vp) | \
            Q(storage_requests__storage_product__provider__in=vp)
        provider_filter = None
        if queryset.model is Project:
            provider_filter = project_filter
        elif queryset.model is Request:
            provider_filter = request_filter

        return queryset.filter(provider_filter).distinct()


class ProvisionProjectViewSet(AbstractListProvisionViewSet):
    """
    class ProvisionProjectViewSet
    """
    permission_classes = (IsCramsAuthenticated,
                          IsActiveProvider)
    serializer_class = provision_serializers.ProvisionProjectSerializer
    queryset = Project.objects.filter(
        current_project__isnull=True, requests__current_request__isnull=True,
        requests__request_status__code__in=PROVISION_ENABLE_REQUEST_STATUS)


class ProvisionRequestViewSet(AbstractListProvisionViewSet):
    """
    class ProvisionRequestViewSet
    """
    permission_classes = (IsCramsAuthenticated,
                          IsActiveProvider)
    serializer_class = provision_serializers.ProvisionRequestSerializer
    queryset = Request.objects.filter(
        request_status__code__in=PROVISION_ENABLE_REQUEST_STATUS,
        current_request__isnull=True,
    )
