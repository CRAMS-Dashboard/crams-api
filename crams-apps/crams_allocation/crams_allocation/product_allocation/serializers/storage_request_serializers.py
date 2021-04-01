# coding=utf-8
"""
Storage Request Serializer
"""
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from crams_allocation.constants.db import REQUEST_STATUS_APPROVED
from crams_allocation.product_allocation.models import StorageRequest
from crams_allocation.serializers.product_request import ProductRequestSerializer
from crams_storage.serializers.storage_product_serializers import StorageProductFetchSerializer
from crams_storage.serializers.storage_product_serializers import StorageProductZoneOnlySerializer
from crams_allocation.product_allocation.serializers.storage_question_serializers import StorageRequestQResponseSerializer


# class StorageRequestSerializer(ProductRequestSerializer):
#     # this one is migrated from d3_prod crams.crams_common.serializers.storage_request_serializers
#     storage_question_responses = StorageRequestQResponseSerializer(many=True, required=False)
#
#     storage_product = StorageProductModelSerializer()
#
#     provision_details = ProvisionDetailsSerializer(required=False)
#
#     provision_id = serializers.SerializerMethodField()
#
#     class Meta(object):
#         model = StorageRequest
#         fields = ['current_quota', 'provision_id', 'storage_product',
#                   'requested_quota_change', 'requested_quota_total',
#                   'approved_quota_change', 'approved_quota_total',
#                   'storage_question_responses', 'provision_details']
#
#         read_only_fields = ['provision_details', 'current_quota']
#
#     @classmethod
#     def get_provision_id(cls, storagerequest_obj):
#         if storagerequest_obj.provision_id:
#             return storagerequest_obj.provision_id.provision_id


class StorageRequestSerializer(ProductRequestSerializer):
    # this one is migrated from d3_prod crams.api.v1.serializers.requestSerializer (line 214)
    """class StorageAllocationSerializer."""

    storage_product = StorageProductZoneOnlySerializer(required=True)

    storage_question_responses = StorageRequestQResponseSerializer(
        many=True, read_only=False, allow_null=True, required=False)

    provision_id = serializers.SlugRelatedField(
        slug_field='provision_id', read_only=True)

    class Meta(object):
        model = StorageRequest
        fields = ('id', 'current_quota', 'provision_id', 'storage_product',
                  'requested_quota_change', 'requested_quota_total',
                  'approved_quota_change', 'approved_quota_total',
                  'storage_question_responses', 'provision_details')
        read_only_fields = ['provision_details', 'current_quota']

    def validate_storage_product(self, data):
        if hasattr(self, 'initial_data'):
            storage_product = self.initial_data.get('storage_product', None)
            if not storage_product or 'id' not in storage_product:
                raise ParseError('Storage product is required')

            storage_product_id = storage_product['id']
            sp_obj = StorageProductFetchSerializer.get_storage_product_obj(
                {'pk': storage_product_id})
        else:
            sp_obj = StorageProductFetchSerializer.get_storage_product_obj(data)
        return sp_obj

    @classmethod
    def reset_provision_details(cls, product_request):
        status_code = product_request.request.request_status.code
        if status_code == REQUEST_STATUS_APPROVED:
            if isinstance(product_request, StorageRequest):
                if product_request.approved_quota_change != 0:
                    return True
        return False

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return storage_request:
        """
        storage_question_responses = validated_data.pop(
            'storage_question_responses', None)

        storage_request = self.Meta.model.objects.create(**validated_data)

        if storage_question_responses:
            for sqr in storage_question_responses:
                sqr_serializer = StorageRequestQResponseSerializer(data=sqr)
                sqr_serializer.is_valid(raise_exception=True)
                sqr_serializer.save(storage_request=storage_request)

        return storage_request
