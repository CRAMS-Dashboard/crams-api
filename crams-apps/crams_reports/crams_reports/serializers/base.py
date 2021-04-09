# coding=utf-8
"""

"""

from crams.serializers.model_serializers import ReadOnlyModelSerializer
from rest_framework import exceptions


class BaseReportSerializer(ReadOnlyModelSerializer):
    USER_ERB_SYSTEMS_CONTEXT_KEY = 'user_erb_system_list'
    CONTACT_CONTEXT_KEY = 'contact'

    def __delete__(self, instance):
        raise exceptions.APIException('Delete not Allowed')

    def create(self, validated_data):
        raise exceptions.APIException('Create not allowed')

    def update(self, instance, validated_data):
        raise exceptions.APIException('Update not allowed')
