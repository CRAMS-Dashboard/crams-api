# coding=utf-8
"""

"""
import copy

from crams.models import EResearchBodyIDKey
from crams.utils.role import AbstractCramsRoleUtils
from crams.serializers import model_serializers
from crams_contact.utils import contact_utils
from crams_collection.models import Project, ProjectID
from crams_collection.config import collection_config as config_init
from crams.serializers import erb_serializers
import logging

from django.db import transaction
from django.contrib import auth
from rest_framework import serializers, exceptions


LOG = logging.getLogger(__name__)
User = auth.get_user_model()


def fetch_project_obj(project_data):
    project_pk = project_data.get('id')
    if not project_pk:
        msg = 'Project primary key field \'id\' is required'
    else:
        try:
            project = Project.objects.get(pk=project_pk)
            if project.current_project:
                project = project.current_project
            return project, None
        except Project.DoesNotExist:
            msg = 'Project does not exist for id {}'.format(project_pk)

    return None, msg


class ERBProjectIDSerializer(erb_serializers.BaseIdentifierSerializer):

    class Meta(object):
        """meta Class."""

        model = ProjectID
        fields = ('identifier', 'system')

    @classmethod
    def build_project_id_list_json(cls, project_id_obj_list):
        def build_json(project, id_list):
            sz = cls(id_list, many=True)
            return {
                'id': project.id,
                'title': project.title,
                'project_ids': sz.data
            }

        project_dict = dict()
        for p_id in project_id_obj_list:
            project_id_list = project_dict.get(p_id.project)
            if not project_id_list:
                project_id_list = list()
                project_dict[p_id.project] = project_id_list
            project_id_list.append(p_id)

        ret_list = list()
        for project_obj, project_id_list in project_dict.items():
            ret_list.append(build_json(project_obj, project_id_list))
        return ret_list

    @classmethod
    def validate_project_identifiers_in_project_list(
            cls, project_data_list, current_user, id_key='project_ids'):
        def build_project_error(project_data, message, id_err_list=None):
            err_dict = copy.copy(project_data)
            err_dict.pop('project_obj', None)
            err_dict['error'] = True
            err_dict['error_message'] = message
            if id_err_list:
                err_dict[id_key] = id_err_list
            return err_dict

        role_fn = contact_utils.fetch_erb_userroles_with_provision_privileges
        user_erb_roles = role_fn(current_user)
        err_list = list()
        for project_data in project_data_list:
            project_ids = project_data.pop(id_key, list())
            project, err_msg = fetch_project_obj(project_data)
            if not project:
                if not err_msg:
                    err_msg = 'Project not found'
                err_list.append(build_project_error(project_data, err_msg))
                continue

            project_data['project_obj'] = project
            id_err_list = list()
            project_id_sz_list = list()
            project_data[id_key] = project_id_sz_list
            context = {
                'project': project,
                'user_erb_roles': user_erb_roles,
                'current_user': current_user
            }
            for sid in project_ids:
                sz = cls(data=sid, context=context)
                sz.is_valid(raise_exception=False)
                if sz.errors:
                    sid['error_message'] = sz.errors
                    id_err_list.append(sid)
                    continue
                project_id_sz_list.append(sz)

            if id_err_list:
                msg = 'Error processing Project Ids'
                err_list.append(build_project_error(
                    project_data, msg, id_err_list))

        if err_list:
            raise exceptions.ValidationError(err_list)

        return project_data_list

    @classmethod
    def update_project_data_list(cls, id_key, project_data_list):
        project_id_obj_list = list()
        for project_data in project_data_list:
            for sz in project_data.get(id_key):
                project_id_obj_list.append(sz.save())

        return project_id_obj_list

    def validate_project(self, validated_data):
        project = validated_data.get('project')
        if not project or not isinstance(project, Project):
            msg = 'Project object must be passed in context'
            raise exceptions.ValidationError(msg)

        self.instance = self.fetch_identifier_unique_for_system(
            validated_data, model=ProjectID)

    @classmethod
    def validate_identifier_for_erb_id(cls, identifier, erb_id_obj):
        key = (erb_id_obj.key, erb_id_obj.e_research_body.name)
        value = config_init.ERBS_PROJECT_ID_UPDATE_FN_MAP.get(key)
        if value:
            generator_fn, validation_fn = value
            identifier = validation_fn(identifier, erb_id_obj)
        return identifier

    def validate(self, data):
        validated_data = dict()
        erb_id_obj = data.get('system')
        validated_data['system'] = erb_id_obj
        validated_data['parent_erb_project_id'] = None

        project = self.context.get('project')
        if project and isinstance(project, Project):
            validated_data['project'] = project
            self.validate_project(validated_data)

        identifier = data.get('identifier')
        validated_data['identifier'] = \
            self.validate_identifier_for_erb_id(identifier, erb_id_obj)
        return validated_data

    def create(self, validated_data):
        self.validate_project(validated_data)
        if self.instance:
            return self.update(self.instance, validated_data)
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        new_instance = self.Meta.model.objects.create(**validated_data)

        # Archive previous value for identifier
        instance.parent_erb_project_id = new_instance
        instance.save()

        # Update archived objects parent_id with latest Identifier object
        qs = ProjectID.objects.filter(parent_erb_project_id=instance)
        if qs.exists():
            for pid in qs.all():
                pid.parent_erb_project_id = new_instance
                pid.save()

        return new_instance


class ProjectIDSearchSerializer(model_serializers.ReadOnlyModelSerializer):
    system = serializers.SlugRelatedField(
        slug_field='key', queryset=EResearchBodyIDKey.objects.all())

    project = serializers.SerializerMethodField()

    class Meta(object):
        """meta Class."""

        model = ProjectID
        fields = ('id', 'system', 'identifier', 'project')

    @classmethod
    def get_project(cls, project_id_obj):
        project = project_id_obj.project
        return {
            'id': project.id,
            'title': project.title
        }
