# coding=utf-8
"""

"""
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from crams_allocation.product_allocation.models import ComputeRequest
from crams_allocation.serializers.product_request import ProductRequestSerializer
from crams_compute.serializers.compute_product import AllocationComputeProductValidate
from crams_allocation.product_allocation.serializers.compute_question_serializer import ComputeQuestionResponseSerializer


class ComputeRequestSerializer(ProductRequestSerializer):
    """
    class ComputeAllocationSerializer
    """

    compute_product = AllocationComputeProductValidate(required=True)

    compute_question_responses = ComputeQuestionResponseSerializer(
        many=True, read_only=False, allow_null=True, required=False)

    remove = serializers.SerializerMethodField()

    class Meta(object):
        model = ComputeRequest
        fields = (
            'id',
            'instances',
            'approved_instances',
            'cores',
            'approved_cores',
            'core_hours',
            'approved_core_hours',
            'compute_product',
            'compute_question_responses',
            'provision_details',
            'remove')
        read_only_fields = ['provision_details']

    @classmethod
    def get_remove(cls, compute_allocation_obj):
        return False

    def validate_compute_product(self, data):
        if hasattr(self, 'initial_data'):
            compute_product = self.initial_data.get('compute_product', None)
            if not compute_product or 'id' not in compute_product:
                raise ParseError('Compute product is required')

            search_dict = {'pk': compute_product.get('id')}
            return AllocationComputeProductValidate.get_compute_product_obj(search_key_dict=search_dict)

        return AllocationComputeProductValidate.get_compute_product_obj(search_key_dict=data)

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return compute_allocation:
        """
        remove = validated_data.pop('remove', False)
        if remove:
            raise ParseError('Code Error: Removed product sent for create')

        compute_question_responses = validated_data.pop(
            'compute_question_responses', None)

        compute_allocation = self.Meta.model.objects.create(**validated_data)
        if compute_question_responses:
            for cqr in compute_question_responses:
                cqr_sz = ComputeQuestionResponseSerializer(data=cqr)
                cqr_sz.is_valid(raise_exception=True)
                cqr_sz.save(compute_allocation=compute_allocation)

        return compute_allocation
