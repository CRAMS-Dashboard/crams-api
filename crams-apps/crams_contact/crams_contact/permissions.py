# coding=utf-8
"""
Crams Permissions
"""

from rest_framework import permissions

from crams_contact.serializers.contact_erb_roles import ContactErbRoleSerializer


class IsServiceManager(permissions.BasePermission):
    """
    Global permission to allow Service Manager role
    """
    message = 'User does not hold Service Manager role.'

    @classmethod
    def role_exists_for_user(cls, user):
        user_roles_dict = ContactErbRoleSerializer.fetch_cramstoken_roles_dict(user)
        if user_roles_dict:
            return ContactErbRoleSerializer.SERVICE_MANAGEMENT_ROLE_TYPE in user_roles_dict
        return False

    def has_permission(self, request, view):
        """
        user has Service Manager role
        :param request:
        :param view:
        :return:
        """
        return self.role_exists_for_user(request.user)
