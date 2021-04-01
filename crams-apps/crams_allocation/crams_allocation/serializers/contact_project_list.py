# coding=utf-8
"""

"""
from django.db.models import Q

from rest_framework import serializers
from crams_contact.models import Contact

from crams_contact.serializers.base_contact_serializer import BaseContactSerializer
from crams_collection.serializers.contact_project_list import AbstractContactProjectListBase


class AdminContactAllocationListSerializer(BaseContactSerializer, AbstractContactProjectListBase):
    projects = serializers.SerializerMethodField()

    contact_ids = serializers.SerializerMethodField()

    class Meta(object):
        model = Contact
        fields = ['id', 'title', 'given_name', 'surname', 'email', 'phone',
                  'organisation', 'orcid', 'scopusid', 'contact_details',
                  'contact_ids', 'latest_contact', 'projects']
        read_only_fields = ['title', 'given_name', 'surname', 'orcid',
                            'scopusid', 'phone', 'organisation',
                            'contact_details', 'latest_contact', 'projects']

    def get_contact(self):
        return self.contact

    def fetch_user_erb_system_list(self):
        return self.user_erb_system_list

    def fetch_project_qs_filter_for_input_erb_systems(self, erb_systems_list):
        if self.user_erb_system_list:
            return Q(requests__e_research_system__in=self.user_erb_system_list)
        return Q()

    @classmethod
    def get_e_research_systems_for_project(cls, project_obj):
        erb_system_set = set()
        request_qs = project_obj.requests.filter(current_request__isnull=True)
        for request in request_qs:
            erb_system_set.add(request.e_research_system)

        ret_list = list()
        for erb_system in erb_system_set:
            ret_list.append({
                'e_research_body': erb_system.e_research_body.name,
                'name': erb_system.name
            })
        return ret_list
