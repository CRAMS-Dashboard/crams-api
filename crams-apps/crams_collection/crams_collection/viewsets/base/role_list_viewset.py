# coding=utf-8
"""

"""
import abc

from rest_framework import viewsets, mixins, exceptions
from rest_framework.decorators import action
from rest_condition import Or

from crams.utils.role import AbstractCramsRoleUtils
from crams_contact.utils import contact_utils
from crams.permissions import IsCramsAdmin
from crams_contact.permissions import IsServiceManager
from crams_collection.permissions import IsProjectFacultyManager
from crams_collection.models import Project
from crams_collection.utils.viewset_utils import ViewsetUtils


class AbstractCramsRoleListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet, ViewsetUtils):
    """
    class AbstractCramsRoleListViewSet
    """
    queryset = Project.objects.none()

    def build_view_response(self, http_request, qs):
        msg = 'Method build_view_response not implemented'
        raise exceptions.APIException(msg)

    @abc.abstractmethod
    def build_null_role_queryset(self, qs, contact):
        """
        subclasses must override this method to provide a meaningful list for normal user
        :param qs:
        :param contact:
        :return:
        """
        raise exceptions.APIException(
            'abstract method not implemented: build_null_role_queryset')

    @abc.abstractmethod
    def build_admin_queryset(self, qs, erbs_list):
        """
        subclasses must override this method to provide a meaningful list for admin user
        :param qs:
        :param erbs_list:
        :return:
        """
        return self.queryset

    @abc.abstractmethod
    def build_faculty_queryset(self, qs, contact):
        """
        subclasses must override this method to provide a meaningful list for faculty user
        :param qs:
        :param contact:
        :return:
        """
        return self.queryset

    @abc.abstractmethod
    def build_department_queryset(self, qs, contact):
        """
        subclasses must override this method to provide a meaningful list for department user
        :param qs:
        :param contact:
        :return:
        """
        return self.queryset

    @abc.abstractmethod
    def build_organisation_queryset(self, qs, contact):
        """
        subclasses must override this method to provide a meaningful list for organisation user
        :param qs:
        :param contact:
        :return:
        """
        return self.queryset

    # default list, for API without roles
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        contact = contact_utils.fetch_user_contact_if_exists(self.request.user)
        if contact:
            qs = self.build_null_role_queryset(qs, contact)

        return self.build_view_response(request, qs)

    @action(detail=False, url_path='admin',
            permission_classes=[Or(IsCramsAdmin, IsServiceManager)])
    def admin_list(self, http_request):
        qs = self.queryset
        erb_system_list = AbstractCramsRoleUtils.get_authorised_e_research_system_list(self.request.user)
        if erb_system_list:
            qs = self.build_admin_queryset(qs, erb_system_list)

        return self.build_view_response(http_request, qs)

    @action(detail=False, url_path='faculty',
            permission_classes=[IsProjectFacultyManager])
    def faculty_list(self, http_request):
        qs = self.queryset
        contact = contact_utils.fetch_user_contact_if_exists(self.request.user)
        if contact:
            qs = self.build_faculty_queryset(qs, contact)

        return self.build_view_response(http_request, qs)

    @action(detail=False, url_path='department',
            permission_classes=[IsCramsAdmin])
    def department_list(self, http_request):
        qs = self.queryset
        contact = contact_utils.fetch_user_contact_if_exists(self.request.user)
        if contact:
            qs = self.build_department_queryset(qs, contact)

        return self.build_view_response(http_request, qs)

    @action(detail=False, url_path='organisation',
            permission_classes=[IsCramsAdmin])
    def organisation_list(self, http_request):
        qs = self.queryset
        contact = contact_utils.fetch_user_contact_if_exists(self.request.user)
        if contact:
            qs = self.build_organisation_queryset(qs, contact)

        return self.build_view_response(http_request, qs)
