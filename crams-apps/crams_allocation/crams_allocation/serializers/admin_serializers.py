# coding=utf-8
"""

"""
from rest_framework import serializers
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.serializers import SlugRelatedField

from crams.constants.api import OVERRIDE_READONLY_DATA
from crams.serializers.lookup_serializers import FundingSchemeSerializer
from crams.utils.validaton_utils import FieldsRequiredValidator, validate_dry_principle
from crams.serializers.utilitySerializers import UpdateOnlyModelSerializer, ProjectAdminField

from crams_allocation.utils import request_utils
from crams.utils import model_lookup_utils
from crams_allocation.constants.db import REQUEST_STATUS_APPROVED
from crams_allocation.constants.db import REQUEST_STATUS_LEGACY_APPROVED
from crams_allocation.constants.db import REQUEST_STATUS_DECLINED
from crams_allocation.constants.db import REQUEST_STATUS_LEGACY_DECLINED
from crams_allocation.constants.db import REQUEST_STATUS_SUBMITTED
from crams_allocation.constants.db import REQUEST_STATUS_UPDATE_OR_EXTEND
from crams_allocation.constants.db import REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED
from crams_allocation.models import Request, AllocationHome
from crams_allocation.serializers.request_serializers import CramsRequestWithoutProjectSerializer
from crams_allocation.serializers.request_serializers import StorageRequestSerializer

from crams_allocation.product_allocation.serializers.compute_request import ComputeRequestSerializer


ADMIN_ENABLE_REQUEST_STATUS = [
    REQUEST_STATUS_SUBMITTED, REQUEST_STATUS_UPDATE_OR_EXTEND]


class BaseAdminSerializer(UpdateOnlyModelSerializer):
    @classmethod
    def get_crams_request_serializer_class(cls):
        return CramsRequestWithoutProjectSerializer

    @classmethod
    def eval_sent_email(cls, validated_data):
        sent_email = validated_data.get('sent_email')
        if type(sent_email) is bool:
            return sent_email
        # if nothing is provided assume default is true
        return True


class ApproveCompReqValid(FieldsRequiredValidator):
    """class ApproveCompReqValid."""

    @classmethod
    def get_fields_required(cls):
        """get Required fields.

        :return:
        """
        return ['approved_instances', 'approved_cores', 'approved_core_hours']

    @classmethod
    def get_fields_unchanged(cls):
        """getFieldsUnchanged.

        :return:
        """
        return [
            'instances', 'cores', 'core_hours', {
                'compute_product': ['id']}]


class ApproveStorReqValid(FieldsRequiredValidator):
    """class ApproveStorReqValid."""

    @classmethod
    def get_fields_required(cls):
        """getFieldsRequired.

        :return:
        """
        return ['approved_quota_change']

    @classmethod
    def get_fields_unchanged(cls):
        """get Fields Unchanged.

        :return:
        """
        return []  # issue 822/ task 823  'quota', {'storage_product': ['id']}]


class DeclineRequestModelSerializer(BaseAdminSerializer):
    """DeclineRequestModelSerializer."""

    project = ProjectAdminField(many=False, read_only=True)
    request_status = SlugRelatedField(
        many=False, read_only=True, slug_field='status')

    class Meta(object):
        """Meta for class DeclineRequestModelSerializer."""

        model = Request
        fields = ['id', 'approval_notes', 'project', 'request_status', 'sent_email']
        read_only_fields = ['request_status', 'project']

    def update(self, instance, validated_data):
        """update.

        :param instance:
        :param validated_data:
        :return: :raise ParseError:
        """
        update_data = dict()
        update_data['approval_notes'] = validated_data.get(
            'approval_notes', None)

        update_data['sent_email'] = self.eval_sent_email(validated_data)

        # copy across the previous data sensitive flag
        update_data['data_sensitive'] = instance.data_sensitive

        context = dict()
        context['request'] = self.context['request']

        # sets the declined status based on the current request status
        if instance.request_status.code == 'E':
            # request_status is read_only, cannot be passed in update_data
            context[OVERRIDE_READONLY_DATA] = {
                'request_status': REQUEST_STATUS_DECLINED}
        elif instance.request_status.code == 'X':
            context[OVERRIDE_READONLY_DATA] = {
                'request_status': REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED}
        elif instance.request_status.code == 'L':
            context[OVERRIDE_READONLY_DATA] = {
                'request_status': REQUEST_STATUS_LEGACY_DECLINED}
        else:
            raise ParseError(
                'Can not decline request when the request_status is: ' +
                str(instance.request_status))

        req_sz_class = self.get_crams_request_serializer_class()
        new_request = req_sz_class(
            instance, data=update_data, partial=True, context=context)
        new_request.is_valid(raise_exception=True)
        return new_request.save()


class ApproveRequestModelSerializer(BaseAdminSerializer):
    """ApproveRequestModelSerializer."""

    project = ProjectAdminField(many=False, read_only=True)
    request_status = serializers.SerializerMethodField()
    compute_requests = ComputeRequestSerializer(
        context=ComputeRequestSerializer.show_error_msg_context(),
        many=True, read_only=False, validators=[
            ApproveCompReqValid()])
    storage_requests = StorageRequestSerializer(
        context=StorageRequestSerializer.show_error_msg_context(),
        many=True, read_only=False, validators=[
            ApproveStorReqValid()])
    funding_scheme = FundingSchemeSerializer(many=False, required=False)
    national_percent = serializers.DecimalField(
        5, 2, max_value=100, min_value=0)
    allocation_home = SlugRelatedField(
        many=False, slug_field='code', required=False, allow_null=True,
        queryset=AllocationHome.objects.all())

    class Meta(object):
        """meta for class ApproveRequestModelSerializer."""

        model = Request
        fields = [
            'id',
            'funding_scheme',
            'national_percent',
            'allocation_home',
            'compute_requests',
            'storage_requests',
            'approval_notes',
            'request_status',
            'start_date',
            'end_date',
            'project',
            'sent_email',
            'data_sensitive']
        read_only_fields = ['request_status', 'start_date', 'end_date', 'project']

    @classmethod
    def get_request_status(cls, request_obj):
        return request_utils.get_erb_request_status_dict(request_obj)

    def validate(self, data):
        """validate.

        :param data:
        :return:
        """
        return data

    def validate_funding_scheme(self, funding_scheme_dict):
        fs_obj = model_lookup_utils.get_funding_scheme_obj(funding_scheme_dict)
        existing_fb = self.instance.funding_scheme.funding_body
        if fs_obj.funding_body != existing_fb:
            raise ValidationError('Funding scheme must belong to ' + existing_fb.name)
        return {'id': fs_obj.id}

    def validate_compute_requests(self, data):
        validate_dry_principle(self, ApproveCompReqValid.get_fields_unchanged(
        ), 'compute_requests', 'Approver')

        return data

    def validate_storage_requests(self, data):
        validate_dry_principle(self, ApproveStorReqValid.get_fields_unchanged(
        ), 'storage_requests', 'Approver')
        return data

    def update(self, instance, validated_data):
        """Update.

        :param instance:
        :param validated_data:
        :return: :raise ParseError:
        """
        update_data = dict()
        update_data['approval_notes'] = validated_data.get('approval_notes')

        funding_scheme_obj = validated_data.get('funding_scheme', None)
        if funding_scheme_obj:
            update_data['funding_scheme'] = funding_scheme_obj

        alloc_home_obj = validated_data.get('allocation_home')
        if alloc_home_obj:
            update_data['allocation_home'] = alloc_home_obj.code
        update_data['national_percent'] = \
            validated_data.get('national_percent')

        update_data['compute_requests'] = self.initial_data.get('compute_requests', None)

        # Storage request has nested classes (zone, product etc) that do not
        # use PrimaryKeyLookup, hence require initial_data to ensure id is
        # passed down
        update_data['storage_requests'] = self.initial_data.get(
            'storage_requests', None)

        update_data['sent_email'] = self.eval_sent_email(validated_data)

        # copy across the previous data sensitive flag
        update_data['data_sensitive'] = instance.data_sensitive

        context = dict()
        context['request'] = self.context['request']
        # only approve where request status code is 'E' or 'X'
        # noinspection PyPep8
        if instance.request_status.code == 'E' or \
                instance.request_status.code == "X":
            # request_status is read_only, cannot be passed in update_data
            context[OVERRIDE_READONLY_DATA] = {
                'request_status': REQUEST_STATUS_APPROVED}
        elif instance.request_status.code == 'L':
            context[OVERRIDE_READONLY_DATA] = {
                'request_status': REQUEST_STATUS_LEGACY_APPROVED}
        else:
            raise ParseError(
                'Can not approve request when the request_status is: ' +
                str(instance.request_status))
        req_sz_class = self.get_crams_request_serializer_class()
        new_request = req_sz_class(
            instance, data=update_data, partial=True, context=context)
        new_request.is_valid(raise_exception=True)
        return new_request.save()
