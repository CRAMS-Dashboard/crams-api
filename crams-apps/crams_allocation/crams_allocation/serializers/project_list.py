# coding=utf-8
"""
Dashboard Serializer definitions
"""
from rest_framework import serializers
from crams_allocation.product_allocation.models import ComputeRequest
from crams_allocation.product_allocation.models import StorageRequest
from crams_allocation.models import Request
from crams_allocation.models import RequestQuestionResponse
from crams.models import EResearchBodyIDKey
from crams_collection.models import Project
from crams.extension import config_init
from crams_allocation.utils import request_utils
from crams.serializers import question_serializers
# from crams.metadata.models import StorageAllocationMetadata # TODO: fix package
from crams_allocation.serializers.product_request import AllocationProvisionDetailsSerializer


READONLY_SZ_CLS = serializers.ModelSerializer


class ProductListAbstract(READONLY_SZ_CLS):
    provision_details = serializers.SerializerMethodField()

    @classmethod
    def get_provision_details(cls, pr_obj):
        pd = pr_obj.provision_details
        if pd:
            return AllocationProvisionDetailsSerializer(pd).data


class AllocationListComputeRequests(ProductListAbstract):
    compute_product = serializers.SerializerMethodField()

    class Meta(object):
        model = ComputeRequest
        fields = ('id', 'instances', 'approved_instances', 'cores',
                  'compute_product', 'approved_cores', 'core_hours',
                  'approved_core_hours', 'provision_details')

    @classmethod
    def get_compute_product(cls, cr_obj):
        cp = cr_obj.compute_product
        if cp:
            return {
                'id': cp.id,
                'name': cp.name
            }


class AllocationListStorageRequests(ProductListAbstract):
    storage_product = serializers.SerializerMethodField()

    class Meta(object):
        model = StorageRequest
        fields = ('id', 'current_quota', 'requested_quota_change',
                  'storage_product', 'requested_quota_total',
                  'approved_quota_change', 'approved_quota_total',
                  'provision_details')

    @classmethod
    def get_storage_product(cls, sr_obj):
        sp = sr_obj.storage_product
        if sp:
            ret_dict = {
                'id': sp.id,
                'name': sp.name,
                'parent_storage_product': None
            }
            if sp.parent_storage_product:
                ret_dict['parent_storage_product'] = {
                    'id': sp.parent_storage_product.id,
                    'name': sp.parent_storage_product.name
                }
            return ret_dict


class AllocationListAllocationSerializer(READONLY_SZ_CLS):
    PROVISION_APPROVE_TUPLE_DICT_KEY = 'approve_provision_dict'

    request_status = serializers.SerializerMethodField()

    funding_scheme = serializers.SerializerMethodField()

    compute_requests = AllocationListComputeRequests(many=True)

    storage_requests = AllocationListStorageRequests(many=True)

    e_research_system = serializers.SerializerMethodField()

    related_allocations = serializers.SerializerMethodField()

    alloc_meta_data = serializers.SerializerMethodField()

    partial_provision_flag = serializers.SerializerMethodField()

    request_question_responses = serializers.SerializerMethodField()

    class Meta(object):
        model = Request
        fields = ('id', 'transaction_id', 'funding_scheme', 'request_status',
                  'e_research_system', 'compute_requests', 'storage_requests',
                  'partial_provision_flag', 'related_allocations',
                  'alloc_meta_data', 'request_question_responses')

    @classmethod
    def get_e_research_system(cls, request_obj):
        erb_system = request_obj.e_research_system
        if erb_system:
            erb_name = erb_system.e_research_body.name
            ret_dict = {
                'id': erb_system.id,
                'name': erb_system.name,
                'e_research_body': erb_name
            }
            if erb_name in config_init.ALLOCATION_LIST_ERB_IDKEY_DICT:
                key_list = config_init.ALLOCATION_LIST_ERB_IDKEY_DICT[erb_name]
                erb_id_qs = EResearchBodyIDKey.objects.filter(
                    e_research_body=erb_system.e_research_body, key__in=key_list)
                project_ids = request_obj.project.project_ids.filter(
                    system__in=erb_id_qs, parent_erb_project_id__isnull=True)
                if project_ids.exists():
                    project_id_dict = dict()
                    ret_dict['project_ids'] = project_id_dict
                    for project_id in project_ids:
                        project_id_dict[project_id.system.key] = project_id.identifier
            return ret_dict

    @classmethod
    def get_request_status(cls, request_obj):
        return request_utils.get_erb_request_status_dict(request_obj)

    def get_related_allocations(self, obj):
        if self.PROVISION_APPROVE_TUPLE_DICT_KEY in self.context:
            pa_dict = self.context.get(self.PROVISION_APPROVE_TUPLE_DICT_KEY)
            related_alloc_tuple = pa_dict.get(obj)
            if related_alloc_tuple and len(related_alloc_tuple) > 1:
                return {
                    'approved_allocation_id': related_alloc_tuple[1],
                    'provisioned_allocation_id': related_alloc_tuple[0]
                }

    @classmethod
    def get_funding_scheme(cls, request_obj):
        funding_scheme = request_obj.funding_scheme
        if funding_scheme:
            return {
                'id': funding_scheme.id,
                'funding_scheme': funding_scheme.funding_scheme
            }

    @classmethod
    def get_alloc_meta_data(cls, request_obj):
        # TODO: uncomment once crams_meta package built
        # if request_obj.current_request:
        #     request_obj = request_obj.current_request
        # qs = StorageAllocationMetadata.objects.filter(
        #     provision_id__storage_requests__request=request_obj,
        #     current_metadata__isnull=True)

        # sr_metadata_count = len(qs)

        # alloc_meta_data = dict(storage_child_count=sr_metadata_count)

        # return alloc_meta_data
        return None

    @classmethod
    def get_partial_provision_flag(cls, request_obj):
        return request_utils.get_partial_provision_flag(request_obj)

    @classmethod
    def get_request_question_responses(cls, request_obj):
        data = RequestQuestionResponseSerializer(
            request_obj.request_question_responses, many=True).data
        return data


class RequestQuestionResponseSerializer(question_serializers.AbstractQuestionResponseSerializer):

    class Meta(object):
        model = RequestQuestionResponse
        fields = ('question', 'question_response')


class AllocationListProjectSerializer(READONLY_SZ_CLS):
    # Request
    requests = serializers.SerializerMethodField()

    historic = serializers.SerializerMethodField(method_name='is_historic')

    class Meta(object):
        model = Project
        fields = ('id', 'crams_id', 'title', 'historic', 'requests')

    @staticmethod
    def is_historic(project_obj):
        return project_obj.current_project is not None

    def get_requests(self, project_obj):
        sz_class = AllocationListAllocationSerializer
        dick_key = sz_class.PROVISION_APPROVE_TUPLE_DICT_KEY
        if dick_key not in self.context:
            e_research_body = None
            if 'e_research_body' in self.context:
                e_research_body = self.context.get('e_research_body')
            self.context[dick_key] = \
                request_utils.get_allocation_approve_provision_objects(
                    e_research_body=e_research_body)
        return sz_class(
            project_obj.requests, many=True, context=self.context).data


'''
from crams import models
p = models.Project.objects.get(pk=164)
from crams.common.serializers import project_list
sz = project_list.AllocationListProjectSerializer(p)
sz.data
'''