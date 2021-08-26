from rest_framework import serializers

from crams_collection.models import ProjectContact
from crams_review import models as review_models


class ReviewDateSerializer(serializers.ModelSerializer):
    review_date = serializers.DateTimeField()
    project = serializers.SerializerMethodField()
    project_contacts = serializers.SerializerMethodField()
    request_id = serializers.SerializerMethodField()
    current_request_id = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    updated_date = serializers.SerializerMethodField()
    status = serializers.CharField()
    notes = serializers.CharField()

    class Meta:
        model = review_models.ReviewDate
        fields = ('id', 'review_date', 'project', 'request_id',
                  'current_request_id', 'updated_by', 'updated_date',
                  'status', 'notes', 'project_contacts')

    def get_project(self, obj):
        # get the latest project title in case it changed
        if obj.request.project.current_project:
            return obj.request.project.current_project.title
        return obj.request.project.title

    def get_project_contacts(self, obj):
        # get latest project contacts
        current_project = obj.request.project
        if obj.request.project.current_project:
            current_project = obj.request.project.current_project

        # get contact role for erb
        r_conf = review_models.ReviewConfig.objects.get(
            e_research_body=obj.request.e_research_system.e_research_body)

        roles = []
        for role in r_conf.contact_roles.all():
            roles.append(role.contact_role)

        # get the project contacts for this review
        prj_contacts = ProjectContact.objects.filter(
            project=current_project,
            contact_role__in=roles
        )

        return ProjectContactSerializer(prj_contacts, many=True).data

    def get_request_id(self, obj):
        return obj.request.id

    def get_current_request_id(self, obj):
        if obj.request.current_request:
            return obj.request.current_request.id
        return None

    def get_updated_by(self, obj):
        if obj.updated_by:
            return obj.updated_by.username
        else:
            return None

    def get_updated_date(self, obj):
        return obj.last_modified_ts


class ProjectContactSerializer(serializers.ModelSerializer):
    contact_id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    contact_role = serializers.SerializerMethodField()

    class Meta:
        model = ProjectContact
        fields = ('id', 'contact_id', 'name', 'email', 'contact_role')

    def get_contact_id(self, obj):
        return obj.contact.id

    def get_name(self, obj):
        if obj.contact.given_name:
            if obj.contact.surname:
                return '{} {}'.format(
                    obj.contact.given_name,
                    obj.contact.surname
                )

        return obj.contact.email

    def get_email(self, obj):
        return obj.contact.email

    def get_contact_role(self, obj):
        return obj.contact_role.name


class ReviewSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    notes = serializers.CharField()

    class Meta:
        model = review_models.ReviewDate
        fields = ('id', 'notes')
