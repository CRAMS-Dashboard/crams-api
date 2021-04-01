# coding=utf-8
"""

"""
from crams.serializers.lookup_serializers import UserSerializer
from rest_framework import response

from crams.permissions import IsCramsAuthenticated
from crams_collection.models import Project
from crams_collection.utils.project_role_querysets import DefaultProjectRoleQueryset
from crams_collection.viewsets.base.role_list_viewset import AbstractCramsRoleListViewSet

# import abc
# class AbstractProjectListViewset(AbstractCramsRoleListViewSet, DefaultProjectRoleQueryset):
#     @classmethod
#     def get_list_serializer_class(cls):
#         msg = 'get_list_serializer_class method not implemented'
#         raise rest_exceptions.APIException(msg)
#
#     @abc.abstractmethod
#     def get_detail_serializer_class(self):
#         msg = 'get_detail_serializer_class method not implemented'
#         raise rest_exceptions.APIException(msg)
#
#     def build_detail_response(self, http_request, pk, qs):
#         if qs.exists():
#             context = {'request': http_request}
#             erb_param = self.get_eresearch_body_param(http_request)
#             if erb_param:
#                 context['e_research_body'] = erb_param
#
#             sz_class = self.get_detail_serializer_class()
#             sz = sz_class(qs.first(), context=context)
#             return response.Response(sz.data)
#
#         model_name = 'object'
#         if hasattr(qs, 'model'):
#             if hasattr(qs.model, '__name__'):
#                 model_name = qs.model.__name__
#         msg = '{} with id {} not available'.format(model_name, pk)
#         raise rest_exceptions.ValidationError(msg)
#
#     def build_detail_route_qs(self, http_request, pk):
#         base_qs = self.queryset
#         qs = base_qs
#         # check if admin
#         erbs_list = AbstractCramsRoleUtils.get_authorised_e_research_system_list(
#             self.request.user)
#         if erbs_list:
#             qs = self.build_admin_queryset(base_qs, erbs_list)
#             qs = qs.filter(pk=pk)
#
#         if not qs.exists():
#             current_user = http_request.user
#             contact = project_user_utils.fetch_user_contact_if_exists(current_user)
#             # check normal user access
#             qs = self.build_null_role_queryset(base_qs, contact)
#             qs = qs.filter(pk=pk)
#             if not qs.exists():
#                 # check faculty access
#                 qs = self.build_faculty_queryset(base_qs, contact)
#                 qs = qs.filter(pk=pk)
#                 if not qs.exists():
#                     # check organisation access
#                     qs = self.build_organisation_queryset(base_qs, contact)
#                     qs = qs.filter(pk=pk)
#                     if not qs.exists():
#                         qs = self.build_department_queryset(base_qs, contact)
#                         qs = qs.filter(pk=pk)
#         return qs


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
        DefaultProjectRoleQueryset.build_faculty_queryset(qs, contact=contact)

    def build_department_queryset(self, qs, contact):
        DefaultProjectRoleQueryset.build_department_queryset(qs, contact=contact)

    def build_organisation_queryset(self, qs, contact):
        DefaultProjectRoleQueryset.build_organisation_queryset(qs, contact=contact)

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