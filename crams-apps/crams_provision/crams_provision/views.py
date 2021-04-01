from rest_framework.response import Response
from rest_framework import mixins, decorators, exceptions
from rest_framework import status

from crams import permissions, models, roleUtils
from crams.provision.serializers import user_id_provision
from crams.common.utils import viewset_utils
from crams.common.utils import user_utils
from crams.provision.serializers import projectid_contact_provision
from crams.provision.serializers import product_provision
from django.db.models import Q


class ProvisionCommonViewSet(viewset_utils.LookupViewset,
                             mixins.UpdateModelMixin):
    permission_classes = [permissions.IsCramsAuthenticated]

    @classmethod
    def get_user_provision_erbs(cls, user_obj, e_research_body_obj=None):
        erb_set = set()
        if isinstance(user_obj, models.User):
            fn = user_utils.fetch_erb_userroles_with_provision_privileges
            user_erb_roles = fn(user_obj, e_research_body_obj)
            for erb_role in user_erb_roles:
                erb_set.add(erb_role.role_erb)
        return list(erb_set)

    @classmethod
    def provision_product_for_http_request(
            cls, http_request, product_data_list, serializer_class):

        sz_list = list()
        context = {'request': http_request}
        for pr_data in product_data_list:
            sz = serializer_class(data=pr_data, context=context)
            sz.is_valid()
            if sz.errors:
                pr_data['errors'] = sz.errors
            else:
                sz_list.append(sz)

        for sz in sz_list:
            sz.save()

        return product_data_list


class ContactProvisionViewSet(ProvisionCommonViewSet):
    permission_classes = [permissions.IsCramsAuthenticated]
    queryset = models.EResearchContactIdentifier.objects.none()
    serializer_class = user_id_provision.ProvisionContactIDSerializer

    @classmethod
    def get_queryset(cls):
        required_status = models.ProvisionDetails.SET_OF_SENT
        qs_filter = Q(provision_details__isnull=True) | Q(
            provision_details__status__in=required_status)
        qs_filter &= Q(parent_erb_contact_id__isnull=True)
        return models.EResearchContactIdentifier.objects.filter(qs_filter)

    @classmethod
    def build_provision_contact_list(cls, valid_erb_list, project=None):
        qs = cls.get_queryset().filter(
            system__e_research_body__in=valid_erb_list)
        if isinstance(project, models.Project):
            qs = qs.filter(contact__project_contacts__project=project)
        return cls.serializer_class.build_contact_id_list_json(qs.distinct())

    def list(self, request, *args, **kwargs):
        erb_obj = self.fetch_e_research_body_param_obj()

        valid_erb_list = self.get_user_provision_erbs(
            self.get_current_user(), erb_obj)
        if valid_erb_list:
            return Response(self.build_provision_contact_list(valid_erb_list))

        msg = 'User does not have required Provider privileges'
        if erb_obj:
            msg = msg + ' for {}'.format(erb_obj.name)
        raise exceptions.ValidationError(msg)

    def retrieve(self, request, *args, **kwargs):
        e_research_body = self.request.query_params.get(
            'e_research_body', None)

        if e_research_body:
            contact = models.Contact.objects.get(pk=kwargs["pk"])
            if contact.system_identifiers.filter(
                    system__e_research_body__name=e_research_body).exists():
                serialize_data = projectid_contact_provision. \
                    ContactIDProvisionSerializer(contact).data
                return Response(serialize_data)
            else:
                # return empty
                return Response({"detail": "No contact ids for ERB"},
                                status=status.HTTP_200_OK)
        else:
            contact = models.Contact.objects.get(pk=kwargs["pk"])
            serialize_data = projectid_contact_provision. \
                ContactIDProvisionSerializer(contact).data
            return Response(serialize_data)

    # @decorators.list_route(methods=['post'], url_path='(?P<pk>\d+)/create')
    def create_user_provision(self, request, *args, **kwargs):
        # get contact
        contact = models.Contact.objects.get(pk=kwargs['pk'])

        # ignore the contact obj changes, focus on changes in contact_ids
        err_cnt_ids = []

        # create the eresearch contact identifier for user
        for req_cnt_id in request.data['contact_ids']:
            try:
                contact_id = models.EResearchContactIdentifier()
                contact_id.contact = contact
                contact_id.identifier = req_cnt_id['identifier']
                contact_id.system_id = req_cnt_id['system']['id']
                contact_id.provisioned = True
                contact_id.save()

            except:
                # unable to save contact id
                err_cnt_ids.append(req_cnt_id['identifier'])

        # display error message
        if err_cnt_ids:
            return Response(
                "Error creating contact_ids, the following"
                " ids were not updated: " + str(err_cnt_ids),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serialize_data = projectid_contact_provision. \
            ContactIDProvisionSerializer(contact).data

        return Response(serialize_data)

    @decorators.action(detail=False, methods=['post'], url_path='(?P<pk>\d+)/update')
    def update_user_provision(self, request, *args, **kwargs):
        # get contact and contact_ids
        contact = models.Contact.objects.get(pk=kwargs['pk'])

        # ignore the contact obj changes, focus on changes in contact_ids
        err_cnt_ids = []

        for req_cnt_id in request.data['contact_ids']:
            try:
                contact_id = models.EResearchContactIdentifier.objects.get(
                    pk=req_cnt_id['id'])

                if contact_id.identifier != req_cnt_id['identifier']:
                    # update contact_id
                    contact_id.identifier = req_cnt_id['identifier']
                    contact_id.provisioned = False
                    contact_id.save()
            except:
                # error couldn't find the matching contact_id
                err_cnt_ids.append(req_cnt_id['identifier'])

        # display error message
        if err_cnt_ids:
            return Response(
                "Error updating contact_ids, the following"
                " ids were not updated: " + str(err_cnt_ids),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serialize_data = projectid_contact_provision. \
            ContactIDProvisionSerializer(contact).data

        return Response(serialize_data)

    @decorators.action(detail=False, methods=['post'], url_path='update')
    def update_provision(self, request, *args, **kwargs):
        ret_data = self.update_provision_data_input(
            request.data, self.get_current_user())
        return Response(ret_data)

    @classmethod
    def update_provision_data_input(cls, data, current_user):
        id_key = 'contact_ids'
        sz_class = user_id_provision.ProvisionContactIDSerializer
        sz_fn = sz_class.validate_contact_identifiers_in_contact_list
        contact_data_list = sz_fn(data, current_user, id_key)

        id_obj_list = sz_class.update_contact_data_list(
            id_key, contact_data_list)

        return sz_class.build_contact_id_list_json(id_obj_list)


class ProjectIDProvisionViewSet(ProvisionCommonViewSet):
    permission_classes = [permissions.IsCramsAuthenticated]
    queryset = models.ProjectID.objects.none()
    serializer_class = projectid_contact_provision.ProvisionProjectIDSerializer

    @decorators.action(detail=False, methods=['get'], url_path='members')
    def project_members(self, request, *args, **kwargs):
        sz_class = projectid_contact_provision.ProjectMemberContactIDList
        erb_obj = self.fetch_e_research_body_param_obj()

        valid_erb_list = self.get_user_provision_erbs(
            self.get_current_user(), erb_obj)
        if valid_erb_list:
            qs = models.Project.objects.filter(
                current_project__isnull=True,
                requests__e_research_system__e_research_body__in=valid_erb_list
            ).distinct()

            context = {'valid_erb_list': valid_erb_list}
            system_obj = self.fetch_system_key_param_obj(erb_obj)
            if system_obj:
                context['system_obj'] = system_obj
            return Response(sz_class(qs, many=True, context=context).data)

        msg = 'User does not have required Provider privileges'
        if erb_obj:
            msg = msg + ' for {}'.format(erb_obj.name)
        raise exceptions.ValidationError(msg)

    def get_queryset(self):
        required_status = models.ProvisionDetails.SET_OF_SENT
        id_filter = Q(provision_details__isnull=True) | Q(
            provision_details__status__in=required_status)
        id_filter &= Q(parent_erb_project_id__isnull=True)
        id_filter &= Q(project__current_project__isnull=True)

        return models.ProjectID.objects.filter(id_filter)

    def list(self, request, *args, **kwargs):
        erb_obj = self.fetch_e_research_body_param_obj()

        valid_erb_list = self.get_user_provision_erbs(
            self.get_current_user(), erb_obj)
        if valid_erb_list:
            qs = self.get_queryset().filter(
                system__e_research_body__in=valid_erb_list)
            return Response(self.serializer_class.
                            build_project_id_list_json(qs))

        msg = 'User does not have required Provider privileges'
        if erb_obj:
            msg = msg + ' for {}'.format(erb_obj.name)
        raise exceptions.ValidationError(msg)

    @decorators.action(detail=False, methods=['post'], url_path='update')
    def update_provision(self, request, *args, **kwargs):
        ret_data = self.update_provision_data_input(
            request.data, self.get_current_user())
        return Response(ret_data)

    @classmethod
    def update_provision_data_input(cls, data, current_user):
        id_key = 'project_ids'
        sz_class = projectid_contact_provision.ProvisionProjectIDSerializer
        project_id_data_list = \
            sz_class.validate_project_identifiers_in_project_list(
                data, current_user, id_key)

        id_obj_list = sz_class.update_project_data_list(
            id_key, project_id_data_list)

        ret_data = sz_class.build_project_id_list_json(id_obj_list)
        return ret_data


class RequestProvisionViewSet(ProvisionCommonViewSet):
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsActiveProvider]
    queryset = models.Request.objects.none()
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
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsActiveProvider]
    queryset = models.StorageRequest.objects.none()
    serializer_class = product_provision.StorageRequestProvisionSerializer

    def get_queryset(self):
        roles_dict = roleUtils.fetch_cramstoken_roles_dict(self.request.user)
        provider_roles = roles_dict.get(roleUtils.PROVIDER_ROLE_KEY)
        user_products = list()
        for product in models.StorageProduct.objects.all():
            if provider_roles and product.provider:
                if product.provider.provider_role in provider_roles:
                    user_products.append(product)
        qs = models.StorageRequest.objects.filter(request__current_request__isnull=True)
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
            sr = models.StorageRequest.objects.get(pk=pk)
        except models.StorageRequest.DoesNotExist:
            return exceptions.ValidationError('Storage Request does not exist for pk {}'.format(pk))

        sz = sz_class(sr, data=http_request.data, context=context)
        sz.is_valid(raise_exception=True)
        return Response(sz_class(sz.save()).data)


class ComputeRequestProvisionViewSet(ProvisionCommonViewSet):
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsActiveProvider]
    queryset = models.ComputeRequest.objects.none()
    serializer_class = product_provision.ComputeRequestProvisionSerializer

    @decorators.action(detail=False, methods=['post'], url_path='update')
    def update_provision(self, request, *args, **kwargs):
        return Response(self.provision_product_for_http_request(
            request, request.data, self.serializer_class))
