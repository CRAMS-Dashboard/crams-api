# coding=utf-8
"""
Role Utilities
"""
import abc
from json import dumps as json_dumps
from json import loads as json_loads
from rest_framework import exceptions

from crams import models
from crams.utils import lang_utils


class AbstractCramsRoleUtils(abc.ABC):
    """
    It is expected that the CramsToken.ks_roles field will be a json dict
      - with the following keys whose values are a list of roles
    The abstract method build_user_roles below should return this dict
    """
    ADMIN_ROLE_KEY = 'admin'
    APPROVER_ROLE_KEY = 'approver'
    PROVIDER_ROLE_KEY = 'provisioner'
    DELEGATE_ROLE_TYPE = 'delegate'
    TENANT_MANAGER = 'tenant_manager'
    SERVICE_MANAGEMENT_ROLE_TYPE = 'service_management'
    FACULTY_MANAGEMENT_ROLE_TYPE = 'faculty_management'
    LEGACY_ROLES_KEY = 'global'

    @abc.abstractmethod
    def build_user_roles(self, user_obj):
        """
        return a dict whose keys are the role KEYs defined above
          - whose values are list of roles
        """
        msg = 'abstract method build_user_roles not implemented'
        raise exceptions.ParseError(msg)

    @classmethod
    def generate_project_role(cls, project_name, role_name):
        return project_name + '_' + role_name

    @classmethod
    def fetch_cramstoken_roles_dict(cls, userobj):
        """
        Fetch roles stored in the DB for given user object
        :param userobj:
        :return:
        """
        if not userobj:
            return None

        # Token could have changed since the user object was fetched.
        #   get latest user object to read latest token
        try:
            current_userobj = models.User.objects.get(pk=userobj.id)
            if current_userobj and hasattr(current_userobj, 'auth_token'):
                auth_token = current_userobj.auth_token
                if hasattr(auth_token, 'cramstoken') and \
                        auth_token.cramstoken.ks_roles:
                    return json_loads(auth_token.cramstoken.ks_roles)
        except models.User.DoesNotExist:
            pass
        return None

    @classmethod
    def get_authorised_e_research_system_list(cls, user, debug=False):
        """

        :param user:
        :return:
        """
        ret_set = set()
        role_dict = cls.fetch_cramstoken_roles_dict(user)
        if debug:
            print('role_dict fetched', role_dict)

        if role_dict:
            if cls.SERVICE_MANAGEMENT_ROLE_TYPE in role_dict:
                return list(models.EResearchBodySystem.objects.all())

            admin_roles = role_dict.get(cls.ADMIN_ROLE_KEY)
            approver_roles = role_dict.get(cls.APPROVER_ROLE_KEY)

            for erbsystem in models.EResearchBodySystem.objects.all():
                if debug:
                    print( '     -- checking for role',
                           erbsystem.admin_role, erbsystem.e_research_body.admin_role, erbsystem.approver_role)
                if admin_roles:
                    if erbsystem.admin_role in admin_roles \
                            or erbsystem.e_research_body.admin_role in admin_roles:
                        ret_set.add(erbsystem)
                if approver_roles and erbsystem.approver_role in approver_roles:
                    ret_set.add(erbsystem)

            if approver_roles:
                for delegate in models.EResearchBodyDelegate.objects.all():
                    if delegate.approver_role in approver_roles:
                        for erbsystem in delegate.e_research_body.systems.all():
                            ret_set.add(erbsystem)

        return list(ret_set)

    @classmethod
    def get_authorised_provider_list(cls, user):
        """

        :param user:
        :return:
        """
        ret_list = list()
        user_roles_dict = cls.fetch_cramstoken_roles_dict(user)
        if user_roles_dict and cls.PROVIDER_ROLE_KEY in user_roles_dict:
            provider_roles = user_roles_dict.get(cls.PROVIDER_ROLE_KEY)
            for p in models.Provider.objects.all():
                if p.provider_role in provider_roles:
                    ret_list.append(p)
        return ret_list

    def setup_crams_token_and_roles(self, user):
        crams_token, created = models.CramsToken.objects.get_or_create(user=user)
        if crams_token.is_expired():  # Expire existing Token
            crams_token.delete()
            crams_token = models.CramsToken(user=user)

        crams_token.ks_roles = json_dumps(self.build_user_roles(user))
        crams_token.save()
        return crams_token

    @classmethod
    def fetch_cramstoken_roles_flatten_to_list(cls, userobj):
        ret_roles_list = list()

        user_roles_dict = cls.fetch_cramstoken_roles_dict(userobj)
        if user_roles_dict:
            for key, roles in user_roles_dict.items():
                if roles:
                    ret_roles_list.append(key)
                    ret_roles_list.extend(roles[:])
        return ret_roles_list

    @classmethod
    def has_e_system_role(cls, user_obj, erb_system_obj=None):
        """

        :param user_obj:
        :param erb_system_obj:
        :return:
        """
        user_roles_dict = cls.fetch_cramstoken_roles_dict(user_obj)
        if user_roles_dict:
            if cls.APPROVER_ROLE_KEY in user_roles_dict:
                if not erb_system_obj:
                    return True
                approver_roles = user_roles_dict.get(cls.APPROVER_ROLE_KEY)
                required_role = erb_system_obj.approver_role
                if approver_roles and required_role in approver_roles:
                    return True

            if cls.ADMIN_ROLE_KEY not in user_roles_dict:
                if not erb_system_obj:
                    return True
                admin_roles = user_roles_dict.get(cls.ADMIN_ROLE_KEY)
                if admin_roles and erb_system_obj.admin_role in admin_roles:
                    return True

        return False

    @classmethod
    def user_has_roles(cls, userobj, role_list):
        role_set = set([lang_utils.strip_lower(role) for role in role_list])
        user_roles_list = cls.fetch_cramstoken_roles_flatten_to_list(userobj)
        if user_roles_list:
            return role_set.issubset(set(user_roles_list))
        return False

    @classmethod
    def user_has_atleast_one_role(cls, userobj, role_list):
        role_set = set([lang_utils.strip_lower(role) for role in role_list])
        user_roles_dict = cls.fetch_cramstoken_roles_dict(userobj)
        if user_roles_dict:
            for key, role in user_roles_dict.items():
                if role in role_set:
                    return True
        return False

    @classmethod
    def is_user_erb_admin(cls, user_obj, erb_obj=None,
                          erb_system_obj=None, include_systems=False):
        user_roles_dict = cls.fetch_cramstoken_roles_dict(user_obj)
        if not user_roles_dict or cls.ADMIN_ROLE_KEY not in user_roles_dict:
            return False
        if erb_obj:
            if not isinstance(erb_obj, models.EResearchBody):
                return False
            admin_role_list = user_roles_dict.get(cls.ADMIN_ROLE_KEY)
            if admin_role_list and erb_obj.admin_role in admin_role_list:
                return True
            if include_systems:
                for erb_system in erb_obj.systems.all():
                    if erb_system.admin_role in admin_role_list:
                        return True
        if erb_system_obj:
            if not isinstance(erb_system_obj, models.EResearchBodySystem):
                return False
            admin_role_list = user_roles_dict.get(cls.ADMIN_ROLE_KEY)
            return admin_role_list and erb_system_obj.admin_role in admin_role_list
        return True

    @classmethod
    def is_user_a_provider(cls, user_obj):
        user_roles_dict = cls.fetch_cramstoken_roles_dict(user_obj)
        return user_roles_dict and cls.PROVIDER_ROLE_KEY in user_roles_dict
