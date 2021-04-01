# coding=utf-8
"""
grant Serializers
"""
import copy

from rest_framework import serializers, exceptions
from crams_collection.models import Grant, GrantType, ArchivableModel
from crams.utils import validaton_utils
from crams.serializers import model_serializers


class MigrateGrantSerializer(model_serializers.CreateOnlyModelSerializer):

    grant_type = serializers.SlugRelatedField(
        slug_field='description', queryset=GrantType.objects.all())

    funding_body_and_scheme = serializers.CharField()

    grant_id = serializers.CharField(required=False)

    start_year = serializers.IntegerField()

    duration = serializers.IntegerField()

    total_funding = serializers.FloatField(required=False)

    class Meta:
        model = Grant
        fields = ('grant_type', 'funding_body_and_scheme', 'grant_id',
                  'start_year', 'duration', 'total_funding')


class GrantTypeLookupSerializer(serializers.Serializer):
    """class GrantTypeLookupSerializer."""
    id = serializers.IntegerField()

    description = serializers.CharField(read_only=True)

    class Meta(object):
        """metaclass."""

        model = GrantType
        fields = ('id', 'description')

    def validate(self, attrs):
        pk = attrs.get('id')
        if not pk:
            raise exceptions.ValidationError('Grant Type id is required')
        qs = GrantType.objects.filter(pk=pk)
        if not qs.exists():
            raise exceptions.ValidationError('Grant Type not found for pk {}'.format(pk))
        return qs.first()


class GrantSerializer(model_serializers.RelatedModelLookupSerializer):

    grant_type = GrantTypeLookupSerializer()

    funding_body_and_scheme = serializers.CharField()

    grant_id = serializers.CharField(required=False, allow_null=True)

    start_year = serializers.IntegerField()

    duration = serializers.IntegerField()

    total_funding = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Grant
        fields = ('grant_type', 'funding_body_and_scheme', 'grant_id',
                  'start_year', 'duration', 'total_funding')
        pk_fields = ('project', 'funding_body_and_scheme', 'grant_type', 'grant_id')

    def save_grant(self, project_obj):
        obj, created = self.Meta.model.objects.get_or_create(**self.validated_data, project=project_obj)
        return obj, created

    @classmethod
    def save_project_grants_return_changes(
            cls, grant_data_dict_list, parent_project, existing_project_instance):
        """

        :param grant_data_dict_list:
        :param parent_project:
        :param existing_project_instance:
        :return: question_response_obj_dict, modified_grants_set, new_grants_set, removed_grants_set
                 - where is question_response_obj_dict is obj_dict[question] = obj
                 - where each grants set is a set of tuple (question, new_response, existing_response)
        """
        existing_grants_dict = dict()
        if existing_project_instance:
            existing_grants = ArchivableModel.get_current_for_qs(
                existing_project_instance.grants.all())
            if existing_grants:
                for new_grant in existing_grants:
                    g_tuple = (new_grant.funding_body_and_scheme, new_grant.grant_type, new_grant.grant_id)
                    existing_grants_dict[g_tuple] = new_grant

        err_list = list()
        sz_list = list()
        ret_obj = validaton_utils.ChangedMetadata()

        if grant_data_dict_list:
            for grant_data_dict in grant_data_dict_list:
                data = copy.copy(grant_data_dict)

                sz = cls(data=data)
                sz.is_valid(raise_exception=False)
                if sz.errors:
                    err_list.append(sz.errors)
                else:
                    sz_list.append(sz)
        if err_list:
            ret_obj.err_list = err_list
            return ret_obj

        obj_dict = dict()
        new_grant_set = set()
        for sz in sz_list:
            new_grant, created = sz.save_grant(project_obj=parent_project)
            g_tuple = (new_grant.funding_body_and_scheme, new_grant.grant_type, new_grant.grant_id)
            obj_dict[g_tuple] = new_grant
            new_grant_set.add(g_tuple)

        add_new_grants_set = set()
        modified_grants_set = set()
        removed_grants_set = set()
        existing_grant_set = set(existing_grants_dict.keys())
        all_grants_set = existing_grant_set | new_grant_set
        for g_tuple in all_grants_set:
            if g_tuple in existing_grant_set and g_tuple in new_grant_set:
                existing_grant = existing_grants_dict[g_tuple]
                new_grant = obj_dict[g_tuple]
                fields_to_check = ['start_year', 'duration', 'total_funding']
                for field in fields_to_check:
                    if getattr(existing_grant, field) == getattr(new_grant, field):
                        continue
                    modified_grants_set.add(g_tuple)
            if g_tuple not in existing_grant_set:
                add_new_grants_set.add(g_tuple)
            elif g_tuple not in new_grant_set:
                removed_grants_set.add(g_tuple)
                existing_pub = existing_grants_dict.get(g_tuple)
                if isinstance(existing_pub, ArchivableModel):
                    existing_pub.archive_instance()

        ret_obj.obj_dict = obj_dict
        ret_obj.modified_related_field_set = modified_grants_set
        ret_obj.removed_related_field_set = removed_grants_set
        ret_obj.new_related_field_set = add_new_grants_set
        return ret_obj
