from json import loads as json_loads

from rest_framework import generics
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from crams.utils.role import AbstractCramsRoleUtils as roleUtils
from crams.permissions import IsCramsAuthenticated
from crams_contact.serializers import contact_serializer


class CurrentUserRolesView(generics.RetrieveAPIView):
    """
        current user roles view
    """
    permission_classes = [IsCramsAuthenticated]

    @classmethod
    def fetch_crams_token_roles(cls, user):
        if not hasattr(user, 'auth_token'):
            raise ParseError('Current user has no token, hence roles not set')

        json_roles = user.auth_token.cramstoken.ks_roles

        if not json_roles:
            return dict()

        return json_loads(json_roles)

    @classmethod
    def convert_user_roles_for_legacy_display(cls, roles):
        roles_dict = {
            roleUtils.APPROVER_ROLE_KEY: roleUtils.APPROVER_ROLE_KEY in roles,
            roleUtils.PROVIDER_ROLE_KEY: roleUtils.PROVIDER_ROLE_KEY in roles,
            roleUtils.ADMIN_ROLE_KEY: roleUtils.ADMIN_ROLE_KEY in roles,
            roleUtils.SERVICE_MANAGEMENT_ROLE_TYPE:
                roleUtils.SERVICE_MANAGEMENT_ROLE_TYPE in roles,
            roleUtils.FACULTY_MANAGEMENT_ROLE_TYPE:
                roleUtils.FACULTY_MANAGEMENT_ROLE_TYPE in roles
        }
        return roles_dict

    @classmethod
    def fetch_erb_user_roles_boolean(cls, contact_obj):
        def init_erb_role_dict():
            return {
                roleUtils.APPROVER_ROLE_KEY: False,
                roleUtils.PROVIDER_ROLE_KEY: False,
                roleUtils.ADMIN_ROLE_KEY: False,
                roleUtils.TENANT_MANAGER: False
            }

        is_manager = hasattr(contact_obj, 'servicemanager') and \
                     contact_obj.servicemanager.active
        is_faculty = contact_obj.manager_faculties.exists() or \
                     contact_obj.manager_organisations.exists()
        erb_role_dict = {
            roleUtils.SERVICE_MANAGEMENT_ROLE_TYPE: is_manager,
            roleUtils.FACULTY_MANAGEMENT_ROLE_TYPE: is_faculty
        }
        if not hasattr(contact_obj, 'user_roles'):
            return erb_role_dict

        for erb_roles in contact_obj.user_roles.filter(
                end_date_ts__isnull=True):
            role_dict = init_erb_role_dict()
            erb_role_dict[erb_roles.role_erb.name.lower()] = role_dict
            is_admin = erb_roles.is_erb_admin or \
                       erb_roles.admin_erb_systems.exists()
            role_dict[roleUtils.ADMIN_ROLE_KEY] = is_admin
            if is_admin:
                role_dict[roleUtils.APPROVER_ROLE_KEY] = True
                role_dict[roleUtils.PROVIDER_ROLE_KEY] = True
            else:
                role_dict[roleUtils.APPROVER_ROLE_KEY] = \
                    erb_roles.approver_erb_systems.exists() or \
                    erb_roles.delegates.exists()
                role_dict[roleUtils.PROVIDER_ROLE_KEY] = \
                    erb_roles.providers.exists()
            role_dict[roleUtils.TENANT_MANAGER] = erb_roles.is_tenant_manager

        return erb_role_dict

    def get(self, request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user = request.user
        ret_dict = dict()
        context = {'request': request}
        contact = contact_serializer.ContactSerializer(context=context).fetch_or_create_given_user_as_contact(user)
        ret_dict['contact'] = contact_serializer.ContactSerializer(contact, context=context).data
        # sz = user_id_provision.ProvisionContactIDSerializer
        # ret_dict['contact_ids'] = \
        #     sz(contact.system_identifiers, context=context, many=True).data

        token_roles = self.fetch_crams_token_roles(user)
        ret_dict['crams_token_roles'] = token_roles
        ret_dict['erb_roles'] = self.fetch_erb_user_roles_boolean(contact)
        ret_dict['user_roles'] = {
            'global': self.convert_user_roles_for_legacy_display(token_roles)
        }
        return Response(ret_dict)
