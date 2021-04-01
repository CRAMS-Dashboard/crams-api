from rest_framework import serializers

from crams.serializers import model_serializers
from crams_log import models


class CramsLogReadOnlySerializer(model_serializers.ReadOnlyModelSerializer):
    id = serializers.IntegerField(required=False)

    message = serializers.CharField(required=False)

    action = serializers.SerializerMethodField()

    type = serializers.SerializerMethodField()

    class Meta(object):
        model = models.CramsLog
        fields = ['id', 'message', 'action', 'type', 'created_by', 'creation_ts']
        read_only_fields = ['message', 'action', 'type', 'created_by', 'creation_ts']

    @classmethod
    def get_action(cls, obj):
        if obj:
            return {
                'action_type': obj.action.action_type,
                'name': obj.action.name
            }
        return None

    @classmethod
    def get_type(cls, obj):
        if obj:
            return {
                'log_type': obj.type.log_type,
                'name': obj.type.name
            }
        return None
