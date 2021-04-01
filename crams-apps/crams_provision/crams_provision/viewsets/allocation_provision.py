# coding=utf-8
"""

"""
from crams.permissions import IsCramsAuthenticated, IsActiveProvider
from crams.utils.role import AbstractCramsRoleUtils
from crams_allocation.models import Request
from crams_allocation.product_allocation.models import StorageRequest, ComputeRequest
from crams_storage.models import StorageProduct
from rest_framework import decorators, exceptions
from rest_framework.response import Response

from crams_provision.serializers import product_provision
from crams_provision.viewsets.base import ProvisionCommonViewSet


class RequestProvisionViewSet(ProvisionCommonViewSet):
    permission_classes = [IsCramsAuthenticated, IsActiveProvider]
    queryset = Request.objects.none()
    serializer_class = product_provision.ProvisionRequestSerializer

    def list(self, request, *args, **kwargs):
        erb_obj = self.fetch_e_research_body_param_obj()

        valid_erb_list = self.get_user_provision_erbs(
            self.get_current_user(), erb_obj)
        if valid_erb_list:
            fn = self.serializer_class.build_provision_request_list_json
            return Response(fn(valid_erb_list))

        msg = 'User does not have required Provider privileges'
        if erb_obj:
            msg = msg + ' for {}'.format(erb_obj.name)
        raise exceptions.ValidationError(msg)

    @decorators.action(detail=False, methods=['post'], url_path='update')
    def update_provision_list(self, http_request, *args, **kwargs):
        ret_data = list()
        for req_data in http_request.data:
            ret_data.append(
                self.provision_request_data(req_data, http_request))
        return Response(ret_data)

    @classmethod
    def provision_request_data(cls, data, http_request):
        ret_data = dict()

        storage_requests = data.get('storage_requests')
        sz_class = product_provision.StorageRequestProvisionSerializer
        if storage_requests:
            ret_data['storage_requests'] = \
                cls.provision_product_for_http_request(
                    http_request, storage_requests, sz_class)

        compute_requests = data.get('compute_requests')
        sz_class = product_provision.ComputeRequestProvisionSerializer
        if compute_requests:
            ret_data['compute_requests'] = \
                cls.provision_product_for_http_request(
                    http_request, compute_requests, sz_class)

        return ret_data


class StorageRequestProvisionViewSet(ProvisionCommonViewSet):
    permission_classes = [IsCramsAuthenticated, IsActiveProvider]
    queryset = StorageRequest.objects.none()
    serializer_class = product_provision.StorageRequestProvisionSerializer

    def get_queryset(self):
        roles_dict = AbstractCramsRoleUtils.fetch_cramstoken_roles_dict(self.request.user)
        provider_roles = roles_dict.get(AbstractCramsRoleUtils.PROVIDER_ROLE_KEY)
        user_products = list()
        for product in StorageProduct.objects.all():
            if provider_roles and product.provider:
                if product.provider.provider_role in provider_roles:
                    user_products.append(product)
        qs = StorageRequest.objects.filter(request__current_request__isnull=True)
        qs = qs.filter(storage_product__in=user_products)
        return qs

    @decorators.action(detail=False, methods=['post'], url_path='update')
    def update_provision(self, request, *args, **kwargs):
        return Response(self.provision_product_for_http_request(
            request, request.data, self.serializer_class))

    @decorators.action(detail=True, methods=['get', 'post'], url_path='update_provision_id')
    def update_provision_id(self, http_request, pk, *args, **kwargs):
        context = {'request': http_request}
        sz_class = product_provision.StorageRequestProvisionIdUpdateSerializer
        self.serializer_class = sz_class
        try:
            sr = StorageRequest.objects.get(pk=pk)
        except StorageRequest.DoesNotExist:
            return exceptions.ValidationError('Storage Request does not exist for pk {}'.format(pk))

        sz = sz_class(sr, data=http_request.data, context=context)
        sz.is_valid(raise_exception=True)
        return Response(sz_class(sz.save()).data)


class ComputeRequestProvisionViewSet(ProvisionCommonViewSet):
    permission_classes = [IsCramsAuthenticated, IsActiveProvider]
    queryset = ComputeRequest.objects.none()
    serializer_class = product_provision.ComputeRequestProvisionSerializer

    @decorators.action(detail=False, methods=['post'], url_path='update')
    def update_provision(self, http_request, *args, **kwargs):
        return Response(self.provision_product_for_http_request(
            http_request, http_request.data, self.serializer_class))
