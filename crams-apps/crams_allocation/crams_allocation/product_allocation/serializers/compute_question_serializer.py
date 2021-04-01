# coding=utf-8
"""

"""

from crams.serializers.question_serializers import BaseQuestionResponseSerializer

from crams_allocation.product_allocation.models import ComputeRequestQuestionResponse


class ComputeQuestionResponseSerializer(BaseQuestionResponseSerializer):
    """class ComputeRequestQuestionResponseSerializer."""

    class Meta(object):
        """meta class."""

        model = ComputeRequestQuestionResponse
        fields = ('id', 'question_response', 'question')
        pk_fields = ['question', 'compute_request']

    @classmethod
    def save_request_question_response(cls, question_response_dict_list, new_parent, old_parent):
        parent_attr_name = 'compute_request'
        old_parent_responses = list()
        if old_parent and old_parent.compute_question_responses.exists():
            old_parent_responses = old_parent.compute_question_responses.all()
        return super().save_question_response(
            question_response_dict_list, new_parent, parent_attr_name, old_parent_responses=old_parent_responses)
