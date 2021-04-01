# coding=utf-8
"""

"""

from abc import ABC

from crams.permissions import IsCramsAdmin
from crams_contact.permissions import IsServiceManager
from rest_condition import Or
from rest_framework.decorators import action

from crams_collection.permissions import IsProjectFacultyManager
from crams_collection.utils.project_role_querysets import DefaultProjectRoleQueryset
from crams_collection.viewsets.base.role_list_viewset import AbstractCramsRoleListViewSet


class AbstractCramsRoleReportViewSet(AbstractCramsRoleListViewSet, DefaultProjectRoleQueryset, ABC):
    """
    class AbstractCramsRoleReportViewSet
    """
    pass


class AbstractCramsReportPrimaryKeyViewSet(AbstractCramsRoleReportViewSet, ABC):

    @action(detail=False, url_path='(?P<pk>\d+)/admin',
            permission_classes=[Or(IsCramsAdmin,
                                   IsServiceManager)])
    def admin_list_pk(self, http_request, pk):
        self.pk_param = pk
        return self.admin_list(http_request)

    @action(detail=False, url_path='(?P<pk>\d+)/faculty',
            permission_classes=[IsProjectFacultyManager])
    def faculty_list_pk(self, http_request, pk):
        self.pk_param = pk
        return self.faculty_list(http_request)

    @action(detail=False, url_path='(?P<pk>\d+)/department',
            permission_classes=[IsCramsAdmin])
    def department_list_pk(self, http_request, pk):
        self.pk_param = pk
        return self.department_list(http_request)

    @action(detail=False, url_path='(?P<pk>\d+)/organisation',
            permission_classes=[IsCramsAdmin])
    def organisation_list_pk(self, http_request, pk):
        self.pk_param = pk
        return self.organisation_list(http_request)
