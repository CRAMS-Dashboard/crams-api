# coding=utf-8
"""
Common ERB related type Serializers
"""

from django.db import transaction

from crams import models
from crams.utils.role import AbstractCramsRoleUtils
from rest_framework import serializers, exceptions
from crams.serializers import model_serializers
from crams.utils import rest_utils


class EResearchBodyIDKeySerializer(model_serializers.ModelLookupSerializer):
    """class EResearchBodyIDKeySerializer."""
    id = serializers.IntegerField(required=False)

    key = serializers.CharField(required=False)

    e_research_body = serializers.SlugRelatedField(
        slug_field='name', required=False,
        queryset=models.EResearchBody.objects.all())

    type = serializers.SerializerMethodField()

    class Meta(object):
        model = models.EResearchBodyIDKey
        field = ('id', 'key', 'e_research_body', 'type')
        pk_fields = ['key', 'e_research_body']
        flags = [model_serializers.ModelLookupSerializer.IGNORE_NOT_EXIST]

    @classmethod
    def build_label_list_for_erb(cls, erb_obj):
        return cls.build_obj_list_for_type(
            erb_obj, obj_type=models.EResearchBodyIDKey.LABEL)

    @classmethod
    def build_metadata_list_for_erb(cls, erb_obj):
        return cls.build_obj_list_for_type(
            erb_obj, obj_type=models.EResearchBodyIDKey.METADATA)

    @classmethod
    def build_idkey_list_for_erb(cls, erb_obj):
        return cls.build_obj_list_for_type(
            erb_obj, obj_type=models.EResearchBodyIDKey.LABEL)

    @classmethod
    def build_obj_list_for_type(cls, erb_obj, obj_type):
        ret_list = list()
        if isinstance(erb_obj, models.EResearchBody):
            qs = models.EResearchBodyIDKey.objects.filter(
                e_research_body=erb_obj, type=obj_type)
            for label in qs:
                ret_list.append(label.key)
        return ret_list

    @classmethod
    def get_type(cls, obj):
        return obj.get_type_display()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        self.verify_field_value('key', attrs, ignore_case=True)
        self.verify_field_value('e_research_body', attrs)
        return self.instance or attrs

    def create_new_metadata(self):
        self.validated_data['type'] = models.EResearchBodyIDKey.METADATA
        return self.create_new()

    # def create_new_label(self):
    #     self.validated_daMETADATAta['type'] = models.EResearchBodyIDKey.LABEL
    #     return self.create_new()

    def create_new_idkey(self):
        self.validated_data['type'] = models.EResearchBodyIDKey.ID_KEY
        return self.create_new()

    # def create_new_for_type(self, obj_type):
    #     if obj_type == models.EResearchBodyIDKey.ID_KEY:
    #         return self.create_new_idkey()
    #     if obj_type == models.EResearchBodyIDKey.METADATA:
    #         return self.create_new_metadata()
    #     return self.create_new_label()

    @transaction.atomic
    def create_new(self):
        if not self.validated_data:
            self.is_valid(raise_exception=True)

        if self.instance:
            erb_obj = self.instance.e_research_body
        else:
            erb_obj = self.validated_data.get('e_research_body')

        # erb label can only be created/updated by admin:
        user, context = rest_utils.get_current_user_from_context(self)
        if not AbstractCramsRoleUtils.is_user_erb_admin(
                user_obj=user, erb_obj=erb_obj, include_systems=True):
            msg = 'User not authorised to add label for erb: {}'
            raise exceptions.ValidationError(msg.format(erb_obj.name))

        if self.instance:
            return self.instance

        description = self.initial_data.get('description')
        if description:
            self.validated_data['description'] = description

        return self.Meta.model.objects.create(**self.validated_data)


class BaseIdentifierSerializer(model_serializers.ReadOnlyModelSerializer):

    system = EResearchBodyIDKeySerializer()

    class Meta(object):
        """meta Class."""

        model = None
        fields = ('identifier', 'system')

    # noinspection PyUnusedLocal
    @classmethod
    def _init_empty(cls, str_val, num):
        ret_dict = dict()
        ret_dict['identifier'] = 'System Identifier'
        ret_dict['system'] = {'e_research_body': 'ERB Name',
                              'key': 'RANDOM_KEY'
                              }
        return ret_dict

    @classmethod
    def _init_from_project_id_data(cls, project_id_data):
        ret_dict = dict()
        ret_dict['identifier'] = project_id_data.get('identifier', None)
        ret_dict['system'] = project_id_data.get('system', None)
        return ret_dict

    @classmethod
    def fetch_identifier_unique_for_system(cls, search_data, model):
        try:
            return model.objects.get(**search_data)
        except model.DoesNotExist:
            pass
        except model.MultipleObjectsReturned:
            msg = 'Unable for find unique {} identifer for {}'
            raise exceptions.ValidationError(msg.format(
                model.__class__, search_data))

    # def get_user_erb_roles(self):
    #     role_fn = user_utils.fetch_erb_userroles_with_provision_privileges
    #     user, context = user_utils.get_current_user_from_context(self)
    #     return role_fn(user)

    def validate_system(self, system_obj):
        if not isinstance(system_obj, models.EResearchBodyIDKey):
            msg = 'Unable to determine system object for {}'
            raise exceptions.ValidationError(msg.format(system_obj))

        erb_required = system_obj.e_research_body

        valid_user = False
        for user_erb_role in self.context.get(
                'user_erb_roles', self.get_user_erb_roles()):
            if user_erb_role.role_erb == erb_required:
                valid_user = True
                break

        is_clone = self.context and 'CLONE' in self.context
        if not valid_user and not is_clone:
            msg = 'User does hold permission to update identifier for {}'
            raise exceptions.ValidationError(msg.format(erb_required))

        return system_obj
