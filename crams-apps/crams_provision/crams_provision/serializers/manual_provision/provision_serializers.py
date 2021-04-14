# coding=utf-8
"""

"""

import logging

from crams.models import ProvisionDetails
from crams.serializers.provision_details_serializer import AbstractProvisionDetailsSerializer
from crams.serializers.provision_details_serializer import ReadOnlyProvisionDetailSerializer
from crams.utils.role import AbstractCramsRoleUtils
from crams_allocation.constants.db import REQUEST_STATUS_APPROVED
from crams_allocation.constants.db import REQUEST_STATUS_LEGACY_APPROVED
from crams_allocation.models import Request
from crams_allocation.product_allocation.models import ComputeRequest, StorageRequest
from crams_allocation.serializers.project_request_serializers import ReadOnlyProjectRequestSerializer
from crams_allocation.serializers.request_serializers import ReadOnlyCramsRequestWithoutProjectSerializer
from crams_allocation.utils import request_utils
from crams_collection.models import ProjectProvisionDetails
from crams_collection.serializers.provision_details import CollectionProvisionDetailsSerializer
from crams_collection.utils import project_user_utils
from crams_contact.models import Contact
from crams_storage.serializers.storage_product_serializers import StorageProductZoneOnlySerializer
from django.db.models import Q
from rest_framework import exceptions
from rest_framework import serializers

from crams_provision.serializers import user_id_provision

PROVISION_ENABLE_REQUEST_STATUS = [
    REQUEST_STATUS_APPROVED, REQUEST_STATUS_LEGACY_APPROVED]

"""
Create a new user for provider  @ http://localhost:8000/admin/auth/user/
  user p001 with password p123  (id set to 15 in migrations,
  so ensure this id is relevant)

Create Crams user, with user id p001

Update Provider and set user for
  Nectar @ http://localhost:8000/admin/api/provider/9/
  select crams user created above 'p001'
  set user active
  ensure provider is set to NeCTAR
  save
  login to API with user p001

"""

LOG = logging.getLogger(__name__)


def fetch_project_provision_list_for_provider(project_obj, provider_list):
    """Fetch project provision list for provider."""
    # TODO refactor: provider has been removed from provision_details
    return project_obj.linked_provisiondetails.all()


def new_provision_detail(current_user, status=ProvisionDetails.SENT):
    return ProvisionDetails.objects.create(
        created_by=current_user,
        updated_by=current_user,
        status=status)

    ##############################################
    # API 1 :  List Products for provisioning    #
    ##############################################


class ProvisionProjectSerializer(ReadOnlyProjectRequestSerializer):
    def get_contact_system_ids(self, project_obj):
        qs = Contact.objects.filter(project_contacts__project=project_obj)
        sz_class = user_id_provision.ProvisionedContactSystemIdentifiers
        return sz_class(qs.distinct(), context=self.context, many=True).data

    """class ProvisionProjectSerializer."""

    def filter_provision_project(self, project_obj):
        """

        :param project_obj:
        :return:
        """
        ret_list = []

        current_user, context = project_user_utils.get_current_user_from_context(self)
        if not AbstractCramsRoleUtils.is_user_a_provider(current_user):
            return ret_list

        pd_context = AbstractProvisionDetailsSerializer.show_error_msg_context()

        status_filter_set = ProvisionDetails.READY_TO_SEND_SET

        context_request = context.get('request')
        new_only = context_request.query_params.get('new_request', None)
        if not new_only:
            status_filter_set = \
                status_filter_set.union(ProvisionDetails.SET_OF_SENT)

        provider_list = AbstractCramsRoleUtils.get_authorised_provider_list(current_user)
        if not provider_list:
            raise exceptions.ValidationError('User is not a provider')
        provider_provision_details = fetch_project_provision_list_for_provider(
            project_obj, provider_list)
        if not provider_provision_details.exists():  # new Project
            project_provision = ProjectProvisionDetails(project=project_obj)
            new_project_pd = new_provision_detail(
                current_user, status=ProvisionDetails.SENT)
            project_provision.provision_details = new_project_pd
            project_provision.save()
            status_filter_set.union(ProvisionDetails.SENT)

        query_set = provider_provision_details.filter(
            provision_details__status__in=status_filter_set)
        for pp in query_set.all():
            pd = pp.provision_details
            if pd.status == ProvisionDetails.POST_PROVISION_UPDATE:
                pd.status = ProvisionDetails.POST_PROVISION_UPDATE_SENT
                pd.save()
            pd_serializer = CollectionProvisionDetailsSerializer(pd, context=pd_context)
            ret_list.append(pd_serializer.data)
        return ret_list

    def filter_requests(self, project_obj):
        """filter requests."""
        ret_list = []

        current_user, context = project_user_utils.get_current_user_from_context(self)
        if not AbstractCramsRoleUtils.is_user_a_provider(current_user):
            return ret_list

        context_request = context.get('request')
        query_params = context_request.query_params
        request_id = query_params.get('request_id', None)
        if request_id:
            # , current_request__isnull=True)
            requests = project_obj.requests.filter(id=request_id)
        else:
            requests = project_obj.requests.filter(
                current_request__isnull=True)

        requests = requests.filter(
            request_status__code=REQUEST_STATUS_APPROVED)

        providers = AbstractCramsRoleUtils.get_authorised_provider_list(current_user)
        provider_filter = \
            Q(compute_requests__compute_product__provider__in=providers) \
            | Q(storage_requests__storage_product__provider__in=providers)

        for req in requests.filter(provider_filter).distinct():
            req_json = ProvisionRequestSerializer(
                req, context=self.context).data
            if req_json:
                if ('compute_requests' in req_json and
                    len(req_json['compute_requests']) > 0) or \
                        ('storage_requests' in req_json and
                         len(req_json['storage_requests']) > 0):
                    ret_list.append(req_json)

        return ret_list


class ProvisionRequestSerializer(ReadOnlyCramsRequestWithoutProjectSerializer):
    request_status = serializers.SerializerMethodField()
    compute_requests = serializers.SerializerMethodField(
        method_name='filter_compute_requests')
    storage_requests = serializers.SerializerMethodField(
        method_name='filter_storage_requests')
    approver_email = serializers.SerializerMethodField()
    partial_provision_flag = serializers.SerializerMethodField()

    class Meta(object):
        model = Request
        fields = ['id', 'funding_scheme', 'funding_body', 'e_research_system', 'request_status',
                  'transaction_id', 'compute_requests', 'storage_requests', 'approver_email',
                  'approval_notes', 'partial_provision_flag']

    @classmethod
    def get_request_status(cls, request_obj):
        return request_utils.get_erb_request_status_dict(request_obj)

    @classmethod
    def get_approver_email(cls, request_obj):
        return request_utils.get_request_approver_email(request_obj)

    @classmethod
    def get_partial_provision_flag(cls, request_obj):
        return request_utils.get_partial_provision_flag(request_obj)

    @classmethod
    def provision_required(cls, product_request):
        if isinstance(product_request, StorageRequest):
            if product_request.approved_quota_change > 0:
                return True
        return False

    def _filter_common(self, base_query_set, get_representation_fn):
        ret_list = []

        current_user, context = project_user_utils.get_current_user_from_context(self)
        if not AbstractCramsRoleUtils.is_user_a_provider(current_user):
            return ret_list

        context_request = context.get('request')
        new_only = context_request.query_params.get('new_request', None)
        filter_provisioned = \
            context_request.query_params.get('filter_provisioned', None)
        query_set = base_query_set

        query_filter = Q()
        if filter_provisioned or new_only:
            query_filter = Q(provision_details__isnull=True) | Q(
                provision_details__status__in=ProvisionDetails.READY_TO_SEND_SET)
            if not new_only:
                query_filter = query_filter | Q(
                    provision_details__status__in=ProvisionDetails.SET_OF_SENT)
        query_set = query_set.filter(query_filter)

        valid_providers = AbstractCramsRoleUtils.get_authorised_provider_list(current_user)
        if base_query_set.model == ComputeRequest:
            query_set = query_set.filter(
                compute_product__provider__in=valid_providers)
        elif base_query_set.model == StorageRequest:
            query_set = query_set.filter(
                storage_product__provider__in=valid_providers)

        for productRequest in query_set:
            ret_list.append(get_representation_fn(productRequest))
            provision_details = productRequest.provision_details
            update_status = ProvisionDetails.READY_TO_SEND_SET
            update_sent_status = ProvisionDetails.POST_PROVISION_UPDATE_SENT

            if provision_details:
                if provision_details.status in update_status:
                    provision_details.status = update_sent_status
                    provision_details.save()
            else:
                # new Product Request
                # - Create new Sent Provision details for Product Request
                pd = new_provision_detail(current_user)
                productRequest.provision_details = pd
                productRequest.save()

        return ret_list

    def filter_compute_requests(self, request_obj):
        """filter compute requests."""

        def get_representation_fn(compute_request_obj):
            """get representation fn."""
            product = compute_request_obj.compute_product
            return {
                'id': compute_request_obj.id,
                'product': {'id': product.id, 'name': product.name},
                'approved_instances': compute_request_obj.approved_instances,
                'approved_cores': compute_request_obj.approved_cores,
                'approved_core_hours': compute_request_obj.approved_core_hours
            }

        return self._filter_common(
            request_obj.compute_requests,
            get_representation_fn)

    def filter_storage_requests(self, request_obj):
        """filter storage requests."""

        def get_representation_fn(storage_request_obj):
            """get representation fn."""
            product_dict = StorageProductZoneOnlySerializer(
                storage_request_obj.storage_product).data
            ret_data = {
                'id': storage_request_obj.id,
                'product': product_dict,
                'approved_quota_change': storage_request_obj.approved_quota_change,
                'current_quota': storage_request_obj.current_quota,
                'approved_quota_total': storage_request_obj.approved_quota_total
            }
            if storage_request_obj.provision_details:
                ret_data['provision_details'] = \
                    ReadOnlyProvisionDetailSerializer(storage_request_obj.provision_details).data

            if storage_request_obj.provision_id:
                ret_data['provision_id'] = \
                    storage_request_obj.provision_id.provision_id

            return ret_data

        return self._filter_common(
            request_obj.storage_requests, get_representation_fn)
