# coding=utf-8
"""
Crams Collection Permissions
"""

from crams.permissions import IsAbstractFacultyManager
from crams.utils.role import AbstractCramsRoleUtils
from rest_framework import permissions

from crams_collection.models import Project


class IsProjectFacultyManager(IsAbstractFacultyManager):
    """
    Global permission to allow faculty Manager role
    """
    message = 'User does not hold Faculty Manager role.'

    @classmethod
    def role_exists_for_user(cls, user_obj):
        exists, _ = cls.user_roles_common(user_obj)
        return exists

    @classmethod
    def user_roles_common(cls, user_obj):
        user_roles_dict = AbstractCramsRoleUtils.fetch_cramstoken_roles_dict(user_obj)

        role_exists = False
        if user_roles_dict:
            role_exists = \
                AbstractCramsRoleUtils.FACULTY_MANAGEMENT_ROLE_TYPE in user_roles_dict
        return role_exists, user_roles_dict

    def has_permission(self, request, view):
        """
        user has Faculty Manager role
        :param request:
        :param view:
        :return:
        """

        role_exists, user_roles_dict = self.user_roles_common(request.user)
        return role_exists

    @classmethod
    def extract_project(cls, obj):
        if isinstance(obj, Project):
            return obj
        # elif isinstance(obj, Request):
        #     project = obj.project
        # elif isinstance(obj, StorageRequest):
        #     project = obj.request.project
        return None

    @classmethod
    def has_access_to_obj(cls, user, obj):
        role_exists, user_roles_dict = cls.user_roles_common(user)
        if not role_exists:
            return False

        project = cls.extract_project(obj)
        if not project:
            return False

        faculty_roles = user_roles_dict[AbstractCramsRoleUtils.FACULTY_MANAGEMENT_ROLE_TYPE]
        if project.department:
            return project.department.faculty.manager_role in faculty_roles
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_access_to_obj(request.user, obj)


class IsProjectContact(permissions.BasePermission):
    """
    Object-level permission to only allow reviewers of an object access to it.
    """

    message = 'User is not listed as contact for the relevant project.'

    @classmethod
    def extract_project(cls, obj):
        if isinstance(obj, Project):
            return obj
        # elif isinstance(obj, Request):
        #     project = obj.project
        return None

    @classmethod
    def common_object_permission(cls, http_request_obj, obj):
        """
        for use by this permission and other friendly classes
        :param http_request_obj:
        :param obj:
        :return:
        """
        project = cls.extract_project(obj)
        if not project:
            return False

        return project.project_contacts.filter(
            contact__email__iexact=http_request_obj.user.email).exists()

    def has_object_permission(self, request, view, obj):
        """
            User has permission to view given project or request object
        :param request:
        :param view:
        :param obj:
        :return:
        """
        return self.common_object_permission(request, obj)
