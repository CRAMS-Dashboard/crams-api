# coding=utf-8
"""
domain Serializers
"""
import copy

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from crams_collection.models import Domain, FORCode
from crams.utils import validaton_utils
from crams.serializers import model_serializers


class MigrateDomainSerializer(model_serializers.CreateOnlyModelSerializer):

    for_code = serializers.SlugRelatedField(
        slug_field='code', queryset=FORCode.objects.all())

    percentage = serializers.FloatField()

    class Meta:
        model = Domain
        fields = ('for_code', 'percentage')


class ForCodeModelRead(model_serializers.ModelLookupSerializer):
    id = serializers.IntegerField()

    code = serializers.CharField(required=False)

    description = serializers.CharField(required=False)

    class Meta(object):
        model = FORCode
        fields = ('id', 'code', 'description')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return self.instance or attrs


class DomainSerializer(model_serializers.RelatedModelLookupSerializer):
    """class DomainSerializer."""
    id = serializers.IntegerField(required=False)

    for_code = ForCodeModelRead()

    percentage = serializers.FloatField()

    class Meta(object):
        model = Domain
        fields = ('id', 'for_code', 'percentage')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        for_code_obj = attrs.get('for_code')
        if not isinstance(for_code_obj, FORCode):
            raise ValidationError('For Code cannot be determined for: {}'.format(for_code_obj))

        return attrs

    def save_for_code_percentage(self, project_obj):
        """

        :return:
        """
        percentage = self.validated_data.pop('percentage')
        obj, created = self.Meta.model.objects.get_or_create(**self.validated_data, project=project_obj)
        if not obj.percentage == percentage:
            obj.percentage = percentage
            obj.save()
        return obj, created

    @classmethod
    def save_parent_domain_return_changes(
            cls, domain_dict_list, parent_project, existing_project_instance):
        """

        :param domain_dict_list:
        :param parent_project:
        :param existing_project_instance:
        :return: domain_obj_dict, modified_for_code_set, new_for_code_set, removed_for_code_set, err_list
                 - where is domain_obj_dict is obj_dict[for_code] = obj
                 - where each for_code set is a set of tuple (for_code, new_percentage, existing_percentage)
        """
        existing_for_code_dict = dict()
        if existing_project_instance:
            for domain in existing_project_instance.domains.all():
                existing_for_code_dict[domain.for_code] = domain

        err_list = list()
        sz_list = list()
        ret_obj = validaton_utils.ChangedMetadata()
        if domain_dict_list:
            for domain_data_dict in domain_dict_list:
                data = copy.copy(domain_data_dict)

                sz = cls(data=data)
                sz.is_valid(raise_exception=False)
                if sz.errors:
                    err_list.append(sz.errors)
                else:
                    sz_list.append(sz)
        if err_list:
            ret_obj.err_list = err_list
            return ret_obj

        new_for_code_dict = dict()
        for sz in sz_list:
            for_code = sz.validated_data.get('for_code')
            percentage = sz.validated_data.get('percentage')
            new_for_code_dict[for_code] = (percentage, sz)

        new_for_code_set = set()
        modified_for_code_set = set()
        removed_for_code_set = set()
        all_for_code = set(list(existing_for_code_dict.keys()) + list(new_for_code_dict.keys()))
        obj_dict = dict()
        for for_code in all_for_code:
            existing_domain = existing_for_code_dict.get(for_code)
            existing_percentage = None
            if existing_domain:
                existing_percentage = existing_domain.percentage

            new_percentage, sz = new_for_code_dict.get(for_code, (None, None))

            if existing_percentage == new_percentage:
                if not parent_project == existing_project_instance:
                    obj, created = sz.save_for_code_percentage(project_obj=parent_project)
                    obj_dict[for_code] = obj
                continue
            if not existing_percentage:
                new_for_code_set.add((for_code, new_percentage, existing_percentage))
                obj, created = sz.save_for_code_percentage(project_obj=parent_project)
                obj_dict[for_code] = obj
            elif not new_percentage:
                removed_for_code_set.add((for_code, new_percentage, existing_percentage))
                if parent_project == existing_project_instance:
                    # delete only if the is update is to existing parent
                    if existing_domain:
                        existing_domain.delete()
            else:
                modified_for_code_set.add((for_code, new_percentage, existing_percentage))
                obj, created = sz.save_for_code_percentage(project_obj=parent_project)
                obj_dict[for_code] = obj

        ret_obj.obj_dict = obj_dict
        ret_obj.modified_related_field_set = modified_for_code_set
        ret_obj.removed_related_field_set = removed_for_code_set
        ret_obj.new_related_field_set = new_for_code_set
        return ret_obj
