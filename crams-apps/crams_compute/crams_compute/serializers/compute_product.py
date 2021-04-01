# coding=utf-8
"""

"""
from crams.serializers import model_serializers
from crams.utils.model_lookup_utils import LookupDataModel
from rest_framework import serializers

from crams_compute.models import ComputeProduct


class AllocationComputeProductValidate(model_serializers.ModelLookupSerializer):
    """
    ==> from d3_prod crams.common.serializers.lookup_serializer
    """
    id = serializers.IntegerField()
    name = serializers.CharField(required=False)

    class Meta(object):
        """metaclass."""
        model = ComputeProduct
        fields = ('id', 'name')

    def validate(self, attrs):
        super().validate(attrs)
        self.verify_field_value('name', attrs, ignore_case=True)
        return attrs

    @classmethod
    def get_compute_product_obj(cls, search_key_dict):
        return LookupDataModel(ComputeProduct).get_lookup_data(search_key_dict)
