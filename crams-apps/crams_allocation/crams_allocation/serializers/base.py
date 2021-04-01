# coding=utf-8
"""

"""
import logging

from crams.models import FundingScheme
from crams.serializers import utilitySerializers, lookup_serializers
from crams_contact.serializers import util_sz
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from crams_allocation.models import AllocationHome
from crams_allocation.models import Request
from crams_allocation.product_allocation.serializers.compute_request import ComputeRequestSerializer
from crams_allocation.product_allocation.serializers.storage_request_serializers import StorageRequestSerializer
from crams_allocation.serializers import question_serializers
from crams_allocation.utils import request_utils

User = get_user_model()
LOG = logging.getLogger(__name__)


class ReadOnlyCramsRequestWithoutProjectSerializer(util_sz.CramsAPIActionStateModelSerializer):

    compute_requests = serializers.SerializerMethodField()

    storage_requests = serializers.SerializerMethodField()

    # request question response
    request_question_responses = serializers.SerializerMethodField()

    request_status = serializers.SerializerMethodField()

    funding_scheme = utilitySerializers.PrimaryKeyLookupField(
        many=False, required=False, allow_null=True,
        fields=['id', 'funding_scheme'], queryset=FundingScheme.objects.all())

    e_research_system = lookup_serializers.EResearchSystemSerializer(
        required=False, allow_null=True)

    funding_body = serializers.SerializerMethodField(method_name='get_fb_name')

    allocation_home = serializers.SlugRelatedField(
        many=False, slug_field='code', required=False, allow_null=True,
        queryset=AllocationHome.objects.all())

    updated_by = serializers.SerializerMethodField()

    historic = serializers.SerializerMethodField(method_name='is_historic')

    readonly = serializers.SerializerMethodField()

    class Meta(object):
        model = Request
        fields = ['id', 'start_date', 'end_date', 'approval_notes', 'historic',
                  'compute_requests', 'storage_requests', 'funding_scheme',
                  'funding_body', 'e_research_system', 'national_percent', 'allocation_home',
                  'transaction_id', 'readonly', 'request_status', 'data_sensitive',
                  'request_question_responses', 'updated_by', 'sent_email', ]

        read_only_fields = ['creation_ts', 'last_modified_ts', 'updated_by',
                            'request_status', 'funding_body', 'transaction_id']

    @staticmethod
    def is_historic(request_obj):
        return request_obj.current_request is not None

    @staticmethod
    def get_fb_name(request_obj):
        if request_obj.funding_scheme:
            return request_obj.funding_scheme.funding_body.name
        return None

    def get_updated_by(self, request_obj):
        return request_utils.BaseRequestUtils.get_restricted_updated_by(
            request_obj, self.get_current_user_crams_token())

    def get_readonly(self, request_obj):
        return self.project_contact_has_readonly_access(request_obj.project, self.contact)

    @classmethod
    def get_request_question_responses(cls, request_obj):
        if request_obj.request_question_responses.exists():
            sz_class = question_serializers.RequestQuestionResponseSerializer
            return sz_class(request_obj.request_question_responses, many=True).data
        return list()

    def get_compute_requests(self, request_obj):
        user = None
        if hasattr(self, 'cramsActionState'):
            user = self.cramsActionState.rest_request.user

        pd_context = ComputeRequestSerializer.build_context_obj(
            user, request_obj.e_research_system)

        ret_list = []
        for c_req in request_obj.compute_requests.all():
            serializer = ComputeRequestSerializer(c_req, context=pd_context)
            data = serializer.data
            data.pop('remove')
            ret_list.append(data)
        return ret_list

    def get_storage_requests(self, request_obj):
        user = None
        if hasattr(self, 'cramsActionState'):
            user = self.cramsActionState.rest_request.user
        pd_context = StorageRequestSerializer.build_context_obj(
            user, request_obj.e_research_system)

        ret_list = []
        for s_req in request_obj.storage_requests.all():
            serializer = StorageRequestSerializer(s_req, context=pd_context)
            ret_list.append(serializer.data)
        return ret_list

    @classmethod
    def get_request_status(cls, request_obj):
        return request_utils.get_erb_request_status_dict(request_obj)

    def get_action_state(self):
        if self.cramsActionState.error_message:
            raise ValidationError(
                'CramsRequestSerializer: ' +
                self.cramsActionState.error_message)
        return self.cramsActionState
