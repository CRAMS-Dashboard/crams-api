# coding=utf-8
"""

"""
from rest_framework import serializers
from rest_framework import exceptions
from crams.serializers import model_serializers

from crams import models as crams_models
from crams_contact import models as contact_models
from crams_contact.serializers import contact_serializer
from crams_collection import models
from crams_collection.log.project_contact_log import ProjectContactLogger
from crams_contact.serializers.base_contact_serializer import BaseContactSerializer


class ProjectContactSerializer(model_serializers.CreateOnlyModelSerializer):
    contact = contact_serializer.CramsContactDetailsLookupSerializer()

    contact_role = serializers.CharField()

    contact_role_id = serializers.IntegerField(required=False)

    contact_role_erb = serializers.SerializerMethodField()

    class Meta(object):
        model = models.ProjectContact
        fields = ('contact', 'contact_role', 'contact_role_id', 'contact_role_erb')

    @classmethod
    def get_contact_role(cls, pc_obj):
        return pc_obj.contact_role.name

    @classmethod
    def get_contact_role_id(cls, pc_obj):
        return pc_obj.contact_role.id

    @classmethod
    def get_contact_role_erb(cls, pc_obj):
        role_erb = pc_obj.contact_role.e_research_body
        if role_erb:
            return pc_obj.contact_role.e_research_body.name

    def add_given_user_as_project_contact(
            self, user_obj, project_obj, role_obj, log_add_contact=False):
        validate_obj_dict = {
            user_obj: crams_models.User,
            project_obj: models.Project,
            role_obj: contact_models.ContactRole
        }
        for obj, cls_obj in validate_obj_dict.items():
            if not isinstance(obj, cls_obj):
                msg = '{} must be of type {}'.format(obj, cls_obj)
                raise exceptions.ValidationError(msg)
        contact_obj = contact_serializer.CramsContactSerializer(context=self.context).\
            fetch_or_create_given_user_as_contact(user_obj)
        pc_obj, created = self.create_project_contact(
            contact_obj, role_obj, project_obj)

        if created and log_add_contact:
            current_user = self.get_current_user()
            ProjectContactLogger.log_project_contact_add(
                project_obj, contact_obj, role_obj, created_by_user_obj=current_user)
        return pc_obj, created

    @classmethod
    def validate_contact(cls, contact_data):
        if not isinstance(contact_data, contact_models.Contact):
            raise exceptions.ValidationError('Unable to determine contact for {}'.format(contact_data))
        return contact_data

    def validate(self, data):
        role_name = data.get('contact_role')
        qs = contact_models.ContactRole.objects.filter(name__iexact=role_name.lower())

        erb_name = None
        if hasattr(self, 'initial_data'):
            erb_name = self.initial_data.get('contact_role_erb')
            if erb_name:
                qs = qs.filter(e_research_body__name=erb_name)
        if not qs.exists():
            msg = '{} Contact role not found for e_research_body {}'
            raise exceptions.ValidationError(msg.format(role_name, erb_name))

        data['contact_role'] = qs.first()
        return data

    @classmethod
    def create_project_contact(cls, contact_obj, role_obj, project_obj):
        pc_obj, created = models.ProjectContact.objects.get_or_create(
            project=project_obj, contact=contact_obj, contact_role=role_obj)
        return pc_obj, created

    @classmethod
    def fetch_if_exists(cls, project_obj, contact_obj, role_obj):
        qs = models.ProjectContact.objects.filter(
            project=project_obj, contact=contact_obj, contact_role=role_obj)
        if qs.exists():
            return qs.first()


