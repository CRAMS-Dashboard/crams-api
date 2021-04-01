# coding=utf-8
"""

"""
from crams_allocation.product_allocation import models
from crams.serializers.question_serializers import BaseQuestionResponseSerializer


class StorageRequestQResponseSerializer(BaseQuestionResponseSerializer):
    """
    ==> from d3_prod crams.common.serializers.question_serializers
    """
    """class StorageRequestQResponseSerializer."""

    class Meta(object):
        model = models.StorageRequestQuestionResponse
        fields = ('id', 'question_response', 'question')
        pk_fields = ['question', 'storage_request']
