# coding=utf-8
"""

"""
from rest_framework import serializers

from crams.models import Question

from crams.serializers import model_serializers


class AbstractQResponseSerializer(model_serializers.CreateOnlyModelSerializer):
    """
    ==> from d3_prod crams.common.serializers.question_serializers
    """
    """class AbstractQResponseSerializer."""

    question = serializers.SlugRelatedField(
        slug_field='key', queryset=Question.objects.all())

    question_response = serializers.CharField()

    class Meta(object):
        model = None
        fields = ('question_response', 'question')
