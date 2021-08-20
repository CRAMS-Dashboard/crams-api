# coding=utf-8
"""

"""
from crams.serializers import model_serializers
from rest_framework import serializers, exceptions

from crams.utils.model_lookup_utils import LookupDataModel
from crams.serializers.lookup_serializers import ZoneSerializer
from crams_storage.models import StorageProduct, StorageType
from crams.serializers.lookup_serializers import EResearchSystemSerializer, FundingBodySerializer, ProviderSerializer


class StorageTypeSerializer(serializers.ModelSerializer):
    """
    ==> from d3_prod crams.common.serializers.lookup_serializers
    """
    """class StorageTypeSerializer."""

    class Meta(object):
        """metaclass."""

        model = StorageType
        fields = ['id', 'storage_type']


class ParentStorageProductSerializer(serializers.ModelSerializer):
    """
    ==> from d3_prod crams.common.serializers.lookup_serializers
    """

    class Meta(object):
        model = StorageProduct
        fields = ['id', 'name']


class StorageProductSerializer(serializers.ModelSerializer):
    """class StorageProductSerializer."""

    storage_type = StorageTypeSerializer(many=False, read_only=True)

    funding_body = FundingBodySerializer(many=False, read_only=True)

    provider = ProviderSerializer(many=False, read_only=True)

    zone = ZoneSerializer(many=False, read_only=True)

    name = serializers.CharField(required=False)

    parent_storage_product = ParentStorageProductSerializer(many=False,
                                                            read_only=True)

    class Meta(object):
        """metaClass."""

        model = StorageProduct
        fields = ['id', 'name', 'storage_type',
                  'funding_body', 'provider', 'zone', 'parent_storage_product']


class StorageProductFetchSerializer(serializers.Serializer):
    """
    ==> from d3_prod crams.common.serializers.storage_request_serializers
    """
    id = serializers.IntegerField(required=True)

    name = serializers.CharField(required=False, allow_null=True)

    class Meta(object):
        fields = ('id', 'name')

    def validate(self, attrs):
        pk = attrs.get('id')
        try:
            sp = StorageProduct.objects.get(pk=pk)
            name = attrs.get('name', None)
            if name and sp.name != name:
                msg = 'Storage Product with id {} has name {}, expected {}'
                raise exceptions.ValidationError(msg.format(pk, sp.name, name))
            attrs['sp_object'] = sp
            return attrs

        except StorageProduct.DoesNotExist:
            msg = 'Storage Product does not exists for id {}'
            raise exceptions.ValidationError(msg.format(pk))

    @classmethod
    def get_storage_product_obj(cls, search_key_dict):
        """
        ==> from d3_prod crams.common.utils import lookup_data
        """
        """

        :param search_key_dict:
        :return:
        """
        return LookupDataModel(StorageProduct).get_lookup_data(search_key_dict)

    @classmethod
    def get_storage_product_lookup_data(cls, search_key_dict):
        """
        ==> from d3_prod crams.common.utils import lookup_data
        """
        """

        :param search_key_dict:
        :param serializer:
        :return:
        """
        return LookupDataModel(StorageProduct).serialize(search_key_dict, cls)


class StorageProductModelSerializer(model_serializers.ModelLookupSerializer):
    """
    ==> from d3_prod crams.common.serializers.storage_request_serializers
    """

    id = serializers.IntegerField()

    name = serializers.CharField(required=False)

    class Meta(object):
        model = StorageProduct
        fields = ('id', 'name')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return self.instance or attrs


class StorageProductZoneOnlySerializer(model_serializers.
                                       ModelLookupSerializer):
    """
    ==> from d3_prod crams.common.serializers.lookup_serializers
    """
    """class StorageProductZoneOnlySerializer."""
    id = serializers.IntegerField()
    storage_type = StorageTypeSerializer(many=False, read_only=True)
    zone = ZoneSerializer(many=False, read_only=True, required=False)
    name = serializers.CharField(required=False)
    parent_storage_product = ParentStorageProductSerializer(
        many=False, read_only=True)

    class Meta(object):
        """metaclass."""
        model = StorageProduct
        fields = ['id', 'name', 'storage_type',
                  'zone', 'parent_storage_product']
        read_only_fields = ['storage_type', 'zone', 'parent_storage_product']

    def validate(self, attrs):
        super().validate(attrs)
        self.verify_field_value('name', attrs, ignore_case=True)
        return attrs


class ERBParentStorageProductSerializer(model_serializers.ReadOnlyModelSerializer):
    class Meta(object):
        model = StorageProduct
        fields = ('id', 'name')


class ERBSystemStorageProductSerializer(model_serializers.ReadOnlyModelSerializer):
    e_research_system = EResearchSystemSerializer()

    storage_type = serializers.SlugRelatedField(
        slug_field='storage_type', read_only=True)

    zone = serializers.SlugRelatedField(slug_field='name', read_only=True)

    parent_storage_product = ERBParentStorageProductSerializer(
        many=False, read_only=True)

    class Meta(object):
        model = StorageProduct
        validators = []
        fields = ('id', 'name', 'e_research_system', 'zone',
                  'storage_type', 'funding_body', 'parent_storage_product')
