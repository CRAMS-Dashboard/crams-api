# coding=utf-8
"""

"""
from crams.serializers.lookup_serializers import UserSerializer
from rest_framework import response

from crams.permissions import IsCramsAuthenticated
from crams_collection.models import Project
from crams_collection.utils.project_role_querysets import DefaultProjectRoleQueryset
from crams_collection.viewsets.base.role_list_viewset import AbstractCramsRoleListViewSet


class ProjectListViewSet(AbstractCramsRoleListViewSet):
    """
    /project_request_list: <BR>
    list all projects linked to the current user <BR>
    /project_request_list/admin: <BR>
    list all projects the user is entitled to see as Crams Admin <BR>
    /project_request_list/faculty: <BR>
    list all projects the user is entitled to see as Faculty manager <BR>
    """

    permission_classes = [IsCramsAuthenticated]
    queryset = Project.objects.none()

    def build_null_role_queryset(self, qs, contact):
        return DefaultProjectRoleQueryset.build_null_role_queryset(qs, contact=contact)

    def build_admin_queryset(self, qs, erbs_list):
        return DefaultProjectRoleQueryset.build_admin_queryset(qs, erbs_list=erbs_list)

    def build_faculty_queryset(self, qs, contact):
        return DefaultProjectRoleQueryset.build_faculty_queryset(qs, contact=contact)

    def build_department_queryset(self, qs, contact):
        return DefaultProjectRoleQueryset.build_department_queryset(qs, contact=contact)

    def build_organisation_queryset(self, qs, contact):
        return DefaultProjectRoleQueryset.build_organisation_queryset(qs, contact=contact)

    @classmethod
    def fetch_project_list_for_qs(cls, project_objects):
        """
        :param project_objects:
        :param user_obj:
        :return:
        """
        project_list = []
        for project in project_objects:
            project_dict = {}
            project_list.append(project_dict)
            project_dict['title'] = project.title
            project_dict['id'] = project.id
        return project_list

    @classmethod
    def build_view_response(cls, http_request, project_qs):
        ret_dict = dict()
        ret_dict['user'] = UserSerializer(http_request.user).data

        if project_qs:
            qs = project_qs.distinct()
            ret_dict['projects'] = cls.fetch_project_list_for_qs(qs)
        return response.Response(ret_dict)