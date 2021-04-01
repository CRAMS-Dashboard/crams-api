# coding=utf-8
"""
Request Question Related Serializers
"""

from crams.serializers.question_serializers import AbstractQResponseSerializer, BaseQuestionResponseSerializer

from crams_allocation.models import RequestQuestionResponse


class RequestQResponseSerializer(AbstractQResponseSerializer):
    """class ProjectQResponseSerializer."""

    class Meta(object):
        model = RequestQuestionResponse
        fields = ('question_response', 'question')


class RequestQuestionResponseSerializer(BaseQuestionResponseSerializer):
    """class RequestQuestionResponseSerializer."""

    class Meta(object):
        """meta class."""

        model = RequestQuestionResponse
        fields = ('id', 'question_response', 'question')
        pk_fields = ['question', 'request']

    @classmethod
    def save_request_question_response(cls, question_response_dict_list, new_parent, old_parent):
        parent_attr_name = 'request'
        old_parent_responses = list()
        if old_parent and old_parent.request_question_responses.exists():
            old_parent_responses = old_parent.request_question_responses.all()
        return super().save_question_response(
            question_response_dict_list, new_parent, parent_attr_name, old_parent_responses=old_parent_responses)
