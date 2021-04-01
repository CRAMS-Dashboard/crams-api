# coding=utf-8
"""

"""
import collections
import logging
from abc import abstractmethod

from crams_contact.models import Contact
from crams_contact.serializers.base_contact_serializer import BaseContactSerializer
from django.contrib import auth
from django.db.models import Q
from rest_framework import serializers, exceptions

from crams_collection import models as collection_models

LOG = logging.getLogger(__name__)
User = auth.get_user_model()


class AbstractContactProjectListBase:
    @abstractmethod
    def get_contact(self):
        raise exceptions.NotFound('method AbstractContactProjectListBase.get_contact not implemented')

    @abstractmethod
    def fetch_user_erb_system_list(self):
        raise exceptions.NotFound('method AbstractContactProjectListBase.fetch_user_erb_system_list not implemented')

    @abstractmethod
    def fetch_project_qs_filter_for_input_erb_systems(self, erb_systems_list):
        raise exceptions.NotFound('method AbstractContactProjectListBase. '
                                  'fetch_project_qs_filter_for_input_erb_systems not implemented')

    @abstractmethod
    def get_e_research_systems_for_project(self, project_obj):
        raise exceptions.NotFound('method AbstractContactProjectListBase.'
                                  'get_e_research_systems_for_project not implemented')

    @classmethod
    def get_provision_status(cls, project):
        try:
            obj = collection_models.ProjectProvisionDetails.objects.get(
                project=project)

            return obj.provision_details.status
        except:
            # if unable to find provision details in current project
            # try searching in child projects if project has ever been provisioned
            current_project = project
            if project.current_project is not None:
                current_project = project.current_project

            child_prjs = collection_models.Project.objects.filter(
                current_project=current_project)

            for prj in child_prjs:
                try:
                    obj = collection_models.ProjectProvisionDetails.objects.get(
                        project=prj)
                    return obj.provision_details.status
                except:
                    continue

            # project has never been provisioned
            return None

    def get_projects(self, contact_obj):
        """
        return projects associated with the given contact_obj
        """
        def build_project(project, project_role_list):
            ret_dict = collections.OrderedDict()
            ret_dict['project'] = {
                'id': project.id,
                'title': project.title
            }
            ret_dict['roles'] = project_role_list
            ret_dict['e_research_systems'] = \
                self.get_e_research_systems_for_project(project)
            ret_dict['provision_status'] = self.get_provision_status(project)
            return ret_dict

        if not contact_obj:
            return list()

        filter_qs = Q(project_contacts__contact=contact_obj,
                      current_project__isnull=True)

        if not contact_obj == self.get_contact():
            # if contact_obj currently being processed does not belong to current user
            #  - show project list only if the current user has admin privileges
            user_erb_system_list = self.fetch_user_erb_system_list()
            if not user_erb_system_list:
                return list()
            filter_qs &= self.fetch_project_qs_filter_for_input_erb_systems(user_erb_system_list)

        qs = collection_models.Project.objects.filter(filter_qs).distinct(). \
            prefetch_related('project_contacts__contact',
                             'project_contacts__contact_role')

        project_list = list()
        for curr_project in qs:
            role_list = list()
            pc_qs = curr_project.project_contacts.filter(contact=contact_obj)
            for pc in pc_qs:
                role = {
                    'id': pc.contact_role.id,
                    'role': pc.contact_role.name
                }
                role_list.append(role)

            project_list.append(build_project(curr_project, role_list))

        return project_list


class ContactProjectListSerializer(BaseContactSerializer, AbstractContactProjectListBase):

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

    def get_e_research_systems_for_project(self, project_obj):
        # currently project is not linked to any erb or erb system
        #  - return empty list
        return list()

    def fetch_project_qs_filter_for_input_erb_systems(self, erb_systems_list):
        # projects are not currently linked to ERB System, so return empty filter
        return Q()
