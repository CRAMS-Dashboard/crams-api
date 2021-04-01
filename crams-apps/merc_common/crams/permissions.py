# coding=utf-8
"""
Crams Permissions
"""
import abc
from rest_framework import permissions, exceptions

from django.conf import settings
from crams.models import CramsToken
from crams.utils.role import AbstractCramsRoleUtils


class IsCramsAuthenticated(permissions.IsAuthenticated):
    """
    Global permission, determine if Curent User has provider role
    """
    message = 'User does not hold valid CramsToken.'

    def has_permission(self, request, view):
        """
        user has a valid cramstoken (not expired)
        :param request:
        :param view:
        :return:
        """
        if super().has_permission(request, view):
            try:
                crams_token = CramsToken.objects.get(user=request.user)
                if crams_token.is_expired():
                    raise exceptions.NotAuthenticated(self.message)
                return True
            except Exception as e:
                pass
        return False


class IsCramsTestSetupUser(IsCramsAuthenticated):
    """
    Global permission, determine if Curent User has provider role
    """
    message = 'User is not authorized to setup test users, ' \
              'update settings.VALID_TEST_SETUP_USER_EMAIL_LIST and check crams token expiry'

    def has_permission(self, request, view):
        """
        user has a valid cramstoken (not expired)
        :param request:
        :param view:
        :return:
        """
        print('in IsCramsTestSetupUser')
        if settings.CURRENT_RUN_ENVIRONMENT.lower() in ['qat', 'staging']:
            if super().has_permission(request, view):
                print('valid emails', settings.VALID_TEST_SETUP_USER_EMAIL_LIST)
                return request.user.email.lower() in settings.VALID_TEST_SETUP_USER_EMAIL_LIST
            else:
                print('User auth failed, either token expired or wrong auth')

        return False


class IsLookupAdmin(permissions.BasePermission):
    """
    Object-level permission to allow Faculty level admin tasks
    """
    message = 'User is not a Faculty Admin'

    def has_object_permission(self, request, view, obj):
        """
        User is assigned as admin to given faculty
        :param request:
        :param view:
        :param faculty obj:
        :return:
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        user_roles_dict = AbstractCramsRoleUtils.fetch_cramstoken_roles_dict(request.user)
        if user_roles_dict:
            return AbstractCramsRoleUtils.ADMIN_ROLE_KEY in user_roles_dict
        return False


class IsCramsAdmin(permissions.BasePermission):
    """
    Global permission to allow CRAMS admin
    """
    message = 'User does not hold Crams Admin role.'

    def has_permission(self, request, view):
        """
        user has CRAMS_ADMIN_ROLE role
        :param request:
        :param view:
        :return:
        """

        user_roles_dict = AbstractCramsRoleUtils.fetch_cramstoken_roles_dict(request.user)
        if user_roles_dict:
            return AbstractCramsRoleUtils.ADMIN_ROLE_KEY in user_roles_dict
        return False

    def has_object_permission(self, request, view, obj):
        return True


class IsServiceManager(permissions.BasePermission):
    """
    Global permission to allow Service Manager role
    """
    message = 'User does not hold Service Manager role.'

    @classmethod
    def role_exists_for_user(cls, user):
        user_roles_dict = AbstractCramsRoleUtils.fetch_cramstoken_roles_dict(user)
        if user_roles_dict:
            return AbstractCramsRoleUtils.SERVICE_MANAGEMENT_ROLE_TYPE in user_roles_dict
        return False

    def has_permission(self, request, view):
        """
        user has Service Manager role
        :param request:
        :param view:
        :return:
        """
        return self.role_exists_for_user(request.user)


class IsAbstractFacultyManager(permissions.BasePermission):
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
        :param self:
        :param request:
        :param view:
        :return:
        """

        role_exists, user_roles_dict = self.user_roles_common(request.user)
        return role_exists

    @abc.abstractmethod
    def has_access_to_obj(self, user, obj):
        msg = 'abstract method has_access_to_obj not implemented'
        raise exceptions.ParseError(msg)

    def has_object_permission(self, request, view, obj):
        return self.has_access_to_obj(request.user, obj)


class IsActiveProvider(permissions.BasePermission):
    """
    Global permission, determine if Curent User has provider role
    """
    message = 'User does not hold Crams Provisioner role.'

    def has_permission(self, request, view):
        """
        user has CRAMS_PROVISIONER_ROLE role
        :param request:
        :param view:
        :return:
        """
        user_roles_dict = AbstractCramsRoleUtils.fetch_cramstoken_roles_dict(request.user)
        if user_roles_dict:
            return AbstractCramsRoleUtils.PROVIDER_ROLE_KEY in user_roles_dict
