# coding=utf-8
"""
Collection Question Related Serializers
"""

from rest_framework import serializers
from crams import models
from crams_collection.models import ProjectQuestionResponse

from crams.serializers.question_serializers import AbstractQResponseSerializer
from crams.serializers.question_serializers import BaseQuestionResponseSerializer


class ProjectQResponseSerializer(AbstractQResponseSerializer):
    """class ProjectQResponseSerializer."""
    question = serializers.SlugRelatedField(
        slug_field='key', queryset=models.Question.objects.all())

    class Meta(object):
        model = ProjectQuestionResponse
        fields = ('question_response', 'question')


class ProjectQuestionResponseSerializer(BaseQuestionResponseSerializer):
    """class ProjectQuestionResponseSerializer."""

    class Meta(object):
        """meta class."""

        model = ProjectQuestionResponse
        fields = ('id', 'question_response', 'question')
        pk_fields = ['question', 'project']

    @classmethod
    def save_project_question_response(cls, question_response_dict_list, new_parent, old_parent):
        parent_attr_name = 'project'
        old_parent_responses = list()
        if old_parent and old_parent.project_question_responses.exists():
            old_parent_responses = old_parent.project_question_responses.all()
        return super().save_question_response(
            question_response_dict_list, new_parent, parent_attr_name, old_parent_responses=old_parent_responses)
