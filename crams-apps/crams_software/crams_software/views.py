from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response

from crams_software import models
from crams.utils import django_utils
from crams.utils import param_utils
from crams_software.serializers import license_agreement
from crams import permissions


class BaseProductView:
    def get_context(self):
        return {'request': self.request}


class SoftwareProductCategoryList(generics.ListAPIView):
    serializer_class = license_agreement.CategoryLookupSerializer
    permission_classes = [permissions.IsCramsAuthenticated]
    queryset = models.SoftwareProductCategory.objects.none()

    def get_queryset(self):
        return models.SoftwareProductCategory.objects.filter(active=True)


class SoftwareLicenseTypeList(generics.ListAPIView):
    serializer_class = license_agreement.TypeLookupSerializer
    permission_classes = [permissions.IsCramsAuthenticated]
    queryset = models.SoftwareLicenseType.objects.none()

    def get_queryset(self):
        return models.SoftwareLicenseType.objects.filter(
            end_date_ts__isnull=True)


class SoftwareProductProvisionList(generics.ListAPIView):
    serializer_class = license_agreement.UserSoftwareProvisionSerializer
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsActiveProvider]

    def get_queryset(self):
        ret_list = list()
        for sp in models.SoftwareProduct.objects.filter(active=True):
            if not sp.licenses.exists():
                if not sp.provision_details:
                    ret_list.append(sp)
                    continue
            qs = sp.licenses.filter(end_date_ts__isnull=True)
            if not qs.exists():
                continue
            ret_list.append(sp)

        return ret_list

    @action(detail=False, methods=['post'], url_path='update')
    def update_provision_status(self, request, *args, **kwargs):
        return Response('Update accepted')


class SoftwareProductList(django_utils.CramsModelViewSet, BaseProductView):
    serializer_class = license_agreement.SoftwareProductSerializer
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsCramsAdmin]
    queryset = models.SoftwareProduct.objects.none()

    def get_queryset(self):
        return models.SoftwareProduct.objects.all()

    def list_common_get_qs(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(active=True)

        params_required_dict = {'current_license_only': []}
        request_params = param_utils.extract_http_query_params(
            params_required_dict, request)
        if 'current_license_only' in request_params:
            qs = qs.filter(
                licenses__isnull=False,
                licenses__end_date_ts__isnull=True)

        qs = qs.prefetch_related('licenses__user_licenses__contact')
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.list_common_get_qs(request, *args, **kwargs)
        return Response(self.serializer_class(
            qs, many=True, context=self.get_context()).data)

    @action(detail=False, url_path='current_user',
            permission_classes=[permissions.IsCramsAuthenticated])
    def user_product_list(self, request, *args, **kwargs):
        qs = self.list_common_get_qs(request, *args, **kwargs)
        sz = license_agreement.UserSoftwareProductSerializer
        return Response(sz(qs, many=True, context=self.get_context()).data)


class LicenseAgreementViewSet(django_utils.CramsModelViewSet, BaseProductView):
    serializer_class = license_agreement.LicenseAgreementSz
    permission_classes = [permissions.IsCramsAuthenticated]
    queryset = models.SoftwareLicense.objects.none()

    def get_queryset(self):
        return models.SoftwareLicense.objects.all()

    def list_common_get_qs(self, request, *args, **kwargs):
        qs = self.get_queryset()

        params_required_dict = {
            'software_id': [param_utils.is_param_numeric_function]
        }
        request_params = param_utils.extract_http_query_params(
            params_required_dict, request)
        software_id = request_params.get('software_id')
        if software_id:
            qs = qs.filter(software__id=software_id)

        return qs

    def list(self, request, *args, **kwargs):
        qs = self.list_common_get_qs(request, *args, **kwargs)
        return Response(self.serializer_class(
            qs, many=True, context=self.get_context()).data)

    @action(detail=False, url_path='current_user',
            permission_classes=[permissions.IsCramsAuthenticated])
    def user_product_list(self, request, *args, **kwargs):
        qs = self.list_common_get_qs(request, *args, **kwargs)
        sz = license_agreement.UserLicenseAgreementListSerializer
        return Response(sz(qs, many=True, context=self.get_context()).data)


class ContactLicenseAgreementViewSet(django_utils.CramsModelViewSet,
                                     BaseProductView):
    serializer_class = license_agreement.ContactLicenseAgreementSz
    permission_classes = [permissions.IsCramsAuthenticated]
    queryset = models.ContactSoftwareLicense.objects.none()

    def get_queryset(self):
        return models.ContactSoftwareLicense.objects.all()

    def list_common_get_qs(self, request, *args, **kwargs):
        model = models.ContactSoftwareLicense
        qs = models.ContactSoftwareLicense.objects.all()

        params_required_dict = {
            'status': [],
        }
        request_params = param_utils.extract_http_query_params(
            params_required_dict, request)
        status = request_params.get('status')
        if status:
            code = model.convert_display_to_status(status)
            if not code:
                msg = 'Status code not found for {}'
                raise exceptions.ValidationError(msg.format(status))
            qs = qs.filter(status=code)

        return qs

    def list(self, request, *args, **kwargs):
        qs = self.list_common_get_qs(request, *args, **kwargs)
        return Response(self.serializer_class(
            qs, many=True, context=self.get_context()).data)

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsCramsAdmin])
    def accept_request(self, request, pk):
        data = {'id': pk}
        sz = self.serializer_class(data=data)
        sz.is_valid(raise_exception=True)
        return Response(sz.accept_user_license())

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsCramsAdmin])
    def decline_request(self, request, pk):
        data = {'id': pk}
        sz = self.serializer_class(data=data)
        sz.is_valid(raise_exception=True)
        return Response(sz.decline_user_license())

    @action(detail=False, url_path='request',
            permission_classes=[permissions.IsCramsAuthenticated,
                                permissions.IsCramsAdmin])
    def request_list(self, request, *args, **kwargs):
        qs = models.ContactSoftwareLicense.objects.all()
        sz = self.serializer_class(
            qs.order_by('-accepted_ts'), many=True,
            context=self.get_context())
        return Response(sz.data)


class SoftwareUsersListViewSet(generics.ListAPIView):
    # serializer_class = license_agreement.ContactLicenseAgreementSz
    serializer_class = license_agreement.ContactSerializer
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsCramsAdmin]
    queryset = models.ContactSoftwareLicense.objects.none()

    def list(self, request, sw_posix_id):
        qs = models.ContactSoftwareLicense.objects.filter(
            license__software__metadata__value=sw_posix_id)

        contact_list = list()
        for csl in qs:
            contact_list.append(csl.contact)

        # get the erb associated with software posix id
        erb = None
        if qs:
            cluster = qs.first().license.cluster.all()
            if cluster:
                erb = cluster.first().e_research_body

        sz = self.serializer_class(contact_list,
                                   many=True,
                                   context={'erb': erb})

        return Response(sz.data)
