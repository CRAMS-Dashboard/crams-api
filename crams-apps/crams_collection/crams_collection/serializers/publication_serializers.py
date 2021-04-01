# coding=utf-8
"""
publication Serializers
"""
import copy
from rest_framework import serializers

from crams import models as crams_models
from crams_collection.models import Publication
from crams.serializers import model_serializers


class MigratePublicationSerializer(model_serializers.CreateOnlyModelSerializer):
    reference = serializers.CharField()

    class Meta:
        model = Publication
        fields = ('reference')


class PublicationSerializer(model_serializers.ModelLookupSerializer):
    """class PublicationSerializer."""
    id = serializers.IntegerField()

    reference = serializers.CharField()

    class Meta(object):
        """meta Class."""

        model = Publication
        fields = ('id', 'reference')
        pk_fields = ('project', 'reference')

    def save_publication(self, project_obj):
        """

        """
        obj, created = self.Meta.model.objects.get_or_create(**self.validated_data, project=project_obj)
        return obj, created

    @classmethod
    def save_project_publication_return_changes(
            cls, publication_list, parent_project, existing_project_instance):
        """

        :param publication_list:
        :param parent_project:
        :param existing_project_instance:
        :return: question_response_obj_dict, modified_publications_set, new_publications_set, removed_publications_set
                 - where is question_response_obj_dict is obj_dict[question] = obj
                 - where each publications set is a set of tuple (question, new_response, existing_response)
        """
        existing_pub_dict = dict()
        if existing_project_instance:
            existing_publications = crams_models.ArchivableModel.get_current_for_qs(
                existing_project_instance.publications.all())
            if existing_publications:
                for pub in existing_publications:
                    existing_pub_dict[pub.reference] = pub

        err_list = list()
        sz_list = list()
        if publication_list:
            for publication_data_dict in publication_list:
                data = copy.copy(publication_data_dict)

                sz = cls(data=data)
                sz.is_valid(raise_exception=False)
                if sz.errors:
                    err_list.append(sz.errors)
                else:
                    sz_list.append(sz)
        if err_list:
            return None, err_list

        new_pub_set = set()
        obj_dict = dict()
        for sz in sz_list:
            obj, created = sz.save_publication(project_obj=parent_project)
            obj_dict[obj.reference] = obj
            new_pub_set.add(obj.reference)

        new_publications_set = set()
        modified_publications_set = set()
        removed_publications_set = set()
        existing_pub_set = set(existing_pub_dict.keys())
        all_pub = existing_pub_set | new_pub_set
        for response in all_pub:
            if response in existing_pub_set and response in new_pub_set:
                continue
            if response not in existing_pub_set:
                new_publications_set.add(response)
            elif response not in new_pub_set:
                removed_publications_set.add(response)
                if parent_project == existing_project_instance:  # archive only if the is update is to existing parent
                    existing_pub = existing_pub_dict.get(response)
                    if isinstance(existing_pub, crams_models.ArchivableModel):
                        existing_pub.archive_instance()

        return obj_dict, modified_publications_set, new_publications_set, removed_publications_set
