# coding=utf-8
"""
Question Related Serializers
"""
import copy

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from crams import models
from crams.serializers import lookup_serializers
from crams.serializers import model_serializers
from crams.utils import validaton_utils


class AbstractQResponseSerializer(model_serializers.CreateOnlyModelSerializer):
    """class AbstractQResponseSerializer."""

    question = serializers.SlugRelatedField(
        slug_field='key', queryset=models.Question.objects.all())

    question_response = serializers.CharField()

    class Meta(object):
        model = None
        fields = ('question_response', 'question')


class AbstractQuestionResponseSerializer(model_serializers.ReadOnlyModelSerializer):
    """class AbstractQuestionResponseSerializer."""
    id = serializers.IntegerField(required=False, read_only=True)

    question = lookup_serializers.QuestionSerializer(required=True)

    question_response = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta(object):
        model = None
        fields = ('id', 'question_response', 'question')

    def validate(self, attrs):
        attrs = super().validate(attrs)

        question_obj = attrs.get('question')
        if not isinstance(question_obj, models.Question):
            raise ValidationError('Question cannot be determined for: {}'.format(question_obj))

        return attrs

    def save_model_question_response(self):
        """
        """
        question_response = self.validated_data.pop('question_response')
        obj, created = self.Meta.model.objects.get_or_create(**self.validated_data)
        if not obj.question_response == question_response:
            obj.question_response = question_response
            obj.save()
        return obj, created

    @classmethod
    def save_parent_question_response_return_changes(
            cls, question_response_dict_list, fill_parent_fn, old_parent_responses, parent_attr_name):
        """

        :param question_response_dict_list:
        :param fill_parent_fn:
        :param old_parent_responses:
        :param parent_attr_name: one of 'project', 'request', 'compute_request', 'storage_request'
            - required for managing delete/archive of question responses
        :return: question_response_obj_dict, modified_questions_set, new_questions_set, removed_questions_set, err_list
                 - where is question_response_obj_dict is obj_dict[question] = obj
                 - where each questions set is a set of tuple (question, new_response, existing_response)
        """
        ret_obj = validaton_utils.ChangedMetadata()
        existing_pqr_dict = dict()
        if old_parent_responses:
            for pqr in old_parent_responses:
                existing_pqr_dict[pqr.question] = (pqr.question_response, getattr(pqr, parent_attr_name))

        err_list = list()
        sz_list = list()
        if question_response_dict_list:
            for question_response_dict in question_response_dict_list:
                data = copy.copy(question_response_dict)

                sz = cls(data=data)
                sz.is_valid(raise_exception=False)
                if sz.errors:
                    err_list.append(sz.errors)
                else:
                    sz_list.append(sz)
        if err_list:
            ret_obj.err_list = err_list
            return ret_obj

        new_pqr_dict = dict()
        for sz in sz_list:
            question = sz.validated_data.get('question')
            question_response = sz.validated_data.get('question_response')
            new_pqr_dict[question] = (question_response, sz)

        new_questions_set = set()
        modified_questions_set = set()
        removed_questions_set = set()
        all_questions = set(list(existing_pqr_dict.keys()) + list(new_pqr_dict.keys()))
        obj_dict = dict()
        for question in all_questions:
            existing_response, existing_parent = None, None
            existing_tuple = existing_pqr_dict.get(question)
            if existing_tuple:
                existing_response, existing_parent = existing_tuple

            new_response, sz = None, None
            new_tuple = new_pqr_dict.get(question)
            if new_tuple:
                new_response, sz = new_pqr_dict.get(question)
                new_parent = fill_parent_fn(sz.validated_data)
            else:
                new_parent = fill_parent_fn(None)

            if existing_response == new_response:
                if not existing_parent == new_parent:
                    obj, created = sz.save_model_question_response()
                    obj_dict[question] = obj
                continue
            if not existing_response:
                new_questions_set.add((question, new_response, existing_response))
                obj, created = sz.save_model_question_response()
                obj_dict[question] = obj
            elif not new_response:
                removed_questions_set.add((question, new_response, existing_response))
                if existing_parent == new_parent:  # archive only if the is update is to existing parent
                    if isinstance(existing_response, models.ArchivableModel):
                        existing_response.archive_instance()
            else:
                modified_questions_set.add((question, new_response, existing_response))
                obj, created = sz.save_model_question_response()
                obj_dict[question] = obj

        ret_obj.obj_dict = obj_dict
        ret_obj.modified_related_field_set = modified_questions_set
        ret_obj.removed_related_field_set = removed_questions_set
        ret_obj.new_related_field_set = new_questions_set
        return ret_obj


class BaseQuestionResponseSerializer(AbstractQuestionResponseSerializer):
    @classmethod
    def save_question_response(
            cls, question_response_dict_list, new_parent, parent_attr_name, old_parent_responses=None):
        """

        :param question_response_dict_list:
        :param new_parent:
        :param parent_attr_name:
        :param old_parent_responses
        :return: sz_dict, err_list
                where sz_dict is (key=sz, value=(___question_response_obj, is_it_add_new, or_update_existing))
                Note: Both add_new and update_existing can be False,
                       - which means this is just a clone of archived parent obj
                    The key sz, has sz.instance object
                     - which if exists, refers to question_response associated with parent
        """
        def fill_parent_fn(data_dict):
            if data_dict:
                data_dict[parent_attr_name] = new_parent
            return new_parent

        return super().save_parent_question_response_return_changes(
            question_response_dict_list, fill_parent_fn, old_parent_responses, parent_attr_name)
