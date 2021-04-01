# coding=utf-8
"""

"""
import abc

from rest_framework import serializers
from rest_framework.exceptions import ParseError

from crams.utils.role import AbstractCramsRoleUtils as RoleUtils

from crams import models
from crams.serializers.model_serializers import ReadOnlyModelSerializer


class ReadOnlyProvisionDetailSerializer(ReadOnlyModelSerializer):
    """
    ==> from d3_prod crams.common.serializers.provision_detail_serializers
    """
    class Meta(object):
        model = models.ProvisionDetails
        fields = ('status', 'message')


class AbstractProvisionDetailsSerializer(serializers.ModelSerializer):
    """
    ==> from d3_prod crams.api.v1.serializers.utilitySerializers
    """
    """class ProvisionDetailsSerializer."""

    SHOW_FAIL_MESSAGE = 'show_fail_message'

    class Meta(object):
        model = models.ProvisionDetails
        abstract = True
        fields = ('id', 'status', 'message')

    @classmethod
    def hide_error_msg_context(cls):
        return {cls.SHOW_FAIL_MESSAGE: False}

    @classmethod
    def show_error_msg_context(cls):
        return {cls.SHOW_FAIL_MESSAGE: True}

    @classmethod
    def build_context_obj(cls, user_obj, erb_system_obj=None):
        if RoleUtils.has_e_system_role(user_obj, erb_system_obj):
            return cls.show_error_msg_context()
        return cls.hide_error_msg_context()

    @classmethod
    def sanitize_provision_details_for_user(cls, provision_details_dict):
        if provision_details_dict.get('status') == models.ProvisionDetails.FAILED:
            provision_details_dict['status'] = models.ProvisionDetails.SENT
            provision_details_dict['message'] = None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context:
            if not self.context.get(self.SHOW_FAIL_MESSAGE, False):
                self.sanitize_provision_details_for_user(data)
        return data

    @abc.abstractmethod
    def _get_new_provision_status(self, existing_status):
        pass

    def create(self, validated_data):
        p_status = validated_data.get('status')

        validated_data['status'] = self._get_new_provision_status(p_status)

        return models.ProvisionDetails.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """

        :param instance:
        :param validated_data:
        :return:
        """
        raise ParseError('models.ProvisionDetails: Update not allowed, clone new ')
