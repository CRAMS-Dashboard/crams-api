# coding=utf-8
"""Lookup Serializers."""
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import serializers, exceptions

# from crams.models import AllocationHome
# from crams.models import ComputeProduct
# from crams.models import ContactRole
# from crams.models import FORCode
from crams.models import FundingBody
from crams.models import FundingScheme
# from crams.models import GrantType
from crams.models import EResearchBodyIDKey
from crams.models import Provider
from crams.models import Question
# from crams.models import RequestStatus
# from crams.models import StorageProduct
# from crams.models import StorageType
from crams.models import SupportEmailContact
from crams.models import Zone
from crams.models import EResearchBodySystem, EResearchBody

from crams.serializers import model_serializers

User = get_user_model()


class QuestionSerializer(model_serializers.ModelLookupSerializer):
    """class QuestionSerializer."""

    id = serializers.IntegerField(required=False)

    key = serializers.CharField()

    question_type = serializers.CharField(required=False)

    question = serializers.CharField(required=False)

    class Meta(object):
        """metaclass."""

        model = Question
        field = ('id', 'key', 'question_type', 'question')
        pk_fields = ['key']
        read_only_fields = ('id', 'question_type', 'question')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return self.instance or attrs


class ProviderSerializer(serializers.ModelSerializer):
    """class ProviderSerializer."""

    class Meta(object):
        """metaclass."""

        model = Provider
        fields = ('id', 'name', 'active')
        # read_only_fields = ('id', 'name')


# class RequestStatusSerializer(serializers.ModelSerializer):
#     """class RequestStatusSerializer."""
#
#     class Meta(object):
#         """metaclass."""
#
#         model = RequestStatus
#         fields = ('id', 'code', 'status')
#

class FundingBodySchemeSerializer(serializers.ModelSerializer):
    """class FundingBodySchemeSerializer"""
    funding_body = serializers.SlugRelatedField(
        slug_field='name', queryset=FundingBody.objects.all())

    class Meta(object):
        """metaclass."""

        model = FundingScheme
        fields = ('funding_scheme', 'funding_body')


class FundingSchemeSerializer(serializers.ModelSerializer):
    """class FundingSchemeSerializer."""

    class Meta(object):
        """metaclass."""

        model = FundingScheme
        fields = ('id', 'funding_scheme')


class FundingBodySerializer(serializers.ModelSerializer):
    """class FundingBodySerializer."""

    class Meta(object):
        """metaclass."""

        model = FundingBody
        fields = ('id', 'name')
        read_only_fields = ('id', 'name')


# class ComputeProductSerializer(serializers.ModelSerializer):
#     """class ComputeProductSerializer."""
#
#     funding_body = FundingBodySerializer(many=False, read_only=True)
#     provider = ProviderSerializer(many=False, read_only=True)
#
#     class Meta(object):
#         """metaclass."""
#
#         model = ComputeProduct
#         fields = ('id', 'name', 'funding_body', 'provider')
#         read_only_fields = ('funding_body', 'provider')
#
#
# class StorageTypeSerializer(serializers.ModelSerializer):
#     """class StorageTypeSerializer."""
#
#     class Meta(object):
#         """metaclass."""
#
#         model = StorageType
#         fields = ('id', 'storage_type')


class ZoneSerializer(serializers.ModelSerializer):
    """class ZoneSerializer."""

    class Meta(object):
        """metaclass."""

        model = Zone
        fields = ('id', 'name')


# class ParentStorageProductSerializer(serializers.ModelSerializer):
#     class Meta(object):
#         model = StorageProduct
#         fields = ('id', 'name')
#
#
# class AllocationComputeProductValidate(model_serializers.ModelLookupSerializer):
#     id = serializers.IntegerField()
#     name = serializers.CharField(required=False)

#     class Meta(object):
#         """metaclass."""
#         model = ComputeProduct
#         fields = ('id', 'name')

#     def validate(self, attrs):
#         super().validate(attrs)
#         self.verify_field_value('name', attrs, ignore_case=True)
#         return attrs
#
#
# class StorageProductZoneOnlySerializer(model_serializers.
#                                        ModelLookupSerializer):
#     """class StorageProductZoneOnlySerializer."""
#     id = serializers.IntegerField()
#     storage_type = StorageTypeSerializer(many=False, read_only=True)
#     zone = ZoneSerializer(many=False, read_only=True, required=False)
#     name = serializers.CharField(required=False)
#     parent_storage_product = ParentStorageProductSerializer(
#         many=False, read_only=True)
#
#     class Meta(object):
#         """metaclass."""
#         model = StorageProduct
#         fields = ('id', 'name', 'storage_type',
#                   'zone', 'parent_storage_product')
#         read_only_fields = ('storage_type', 'zone', 'parent_storage_product')
#
#     def validate(self, attrs):
#         super().validate(attrs)
#         self.verify_field_value('name', attrs, ignore_case=True)
#         return attrs
#
#
# class StorageProductSerializer(serializers.ModelSerializer):
#     """class StorageProductSerializer."""
#
#     storage_type = StorageTypeSerializer(many=False, read_only=True)
#
#     funding_body = FundingBodySerializer(many=False, read_only=True)
#
#     provider = ProviderSerializer(many=False, read_only=True)
#
#     zone = ZoneSerializer(many=False, read_only=True)
#
#     name = serializers.CharField(required=False)
#
#     parent_storage_product = ParentStorageProductSerializer(many=False,
#                                                             read_only=True)
#
#     class Meta(object):
#         """metaClass."""
#
#         model = StorageProduct
#         fields = ('id', 'name', 'storage_type',
#                   'funding_body', 'provider', 'zone', 'parent_storage_product')
#
#
# class GrantTypeSerializer(serializers.ModelSerializer):
#     """class GrantTypeSerializer."""
#
#     class Meta(object):
#         """metaclass."""
#
#         model = GrantType
#         fields = ('id', 'description')
#

class EResearchBodyIDKeySerializer(serializers.ModelSerializer):
    """class EResearchBodyIDKeySerializer."""

    class Meta(object):
        """metaclass."""

        model = EResearchBodyIDKey
        field = ('id', 'key')


#
#
# class ContactRoleSerializer(serializers.ModelSerializer):
#     """class ContactRoleSerializer."""
#
#     class Meta(object):
#         """metaclass."""
#
#         model = ContactRole
#         field = ('id', 'name')


class SupportEmailContactSerializer(serializers.ModelSerializer):
    """Class SupportEmailContactSerializer."""
    e_research_body = serializers.SerializerMethodField()
    e_research_system = serializers.SerializerMethodField()

    class Meta(object):
        """metaclass."""

        model = SupportEmailContact
        fields = ('id', 'description', 'email',
                  'e_research_body', 'e_research_system')

    @classmethod
    def get_e_research_body(cls, obj):
        return obj.e_research_body.name

    @classmethod
    def get_e_research_system(cls, obj):
        if obj.e_research_system:
            return obj.e_research_system.name
        else:
            return None


#
#
# class FORCodeSerializer(serializers.ModelSerializer):
#     """class FORCodeSerializer."""
#
#     class Meta(object):
#         """metaclass."""
#
#         model = FORCode
#         fields = ('id', 'code', 'description')
#
#
# class AllocationHomeSerializer(serializers.ModelSerializer):
#     """class AllocationHomeSerializer."""
#
#     class Meta(object):
#         """metaclass."""
#
#         model = AllocationHome
#         fields = ('id', 'code', 'description')


class UserSerializer(serializers.ModelSerializer):
    """class UserSerializer."""

    class Meta(object):
        """metaclass."""

        model = User
        fields = ('first_name', 'last_name', 'email')  # , 'auth_token')


class EResearchBodySerializer(serializers.ModelSerializer):
    """class EResearchBodySerializer."""

    class Meta(object):
        """metaclass."""

        model = EResearchBody
        fields = ('name')
        read_only_fields = ('name')


class EResearchSystemSerializer(model_serializers.ReadOnlyModelSerializer):
    """class EResearchSystemSerializer."""
    e_research_body = serializers.SlugRelatedField(
        slug_field='name', queryset=EResearchBody.objects.all())

    class Meta(object):
        """metaclass."""

        model = EResearchBodySystem
        validators = []
        fields = ('id', 'name', 'e_research_body')

    def fetch_object(self):
        try:
            return EResearchBodySystem.objects.get(
                name=self.name, e_research_body=self.e_research_body)
        except Exception as e:
            pass
        return None
#
#
# class ERBSystemComputeProductSerializer(model_serializers.
#                                         ReadOnlyModelSerializer):
#     """class ComputeProductSerializer."""
#
#     e_research_system = EResearchSystemSerializer()
#
#     funding_body = \
#         serializers.SlugRelatedField(slug_field='name', read_only=True)
#
#     class Meta(object):
#         """metaclass."""
#
#         model = ComputeProduct
#         validators = []
#         fields = ('id', 'name', 'e_research_system', 'funding_body')
#
#
# class EResearchBodyParentStorageProductSerializer(model_serializers.
#                                                   ReadOnlyModelSerializer):
#     class Meta(object):
#         model = StorageProduct
#         fields = ('id', 'name')
#
#
# class ERBSystemStorageProductSerializer(model_serializers.
#                                         ReadOnlyModelSerializer):
#     e_research_system = EResearchSystemSerializer()
#
#     storage_type = serializers.SlugRelatedField(
#         slug_field='storage_type', read_only=True)
#
#     zone = serializers.SlugRelatedField(slug_field='name', read_only=True)
#
#     parent_storage_product = EResearchBodyParentStorageProductSerializer(
#         many=False, read_only=True)
#
#     class Meta(object):
#         model = StorageProduct
#         validators = []
#         fields = ('id', 'name', 'e_research_system', 'zone',
#                   'storage_type', 'funding_body', 'parent_storage_product')
