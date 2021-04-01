# coding=utf-8
"""
Common Utils type Serializers
"""
# import ast
import pprint

from rest_framework import serializers, exceptions

from crams.utils import rest_utils, action_state
from crams_contact.utils import contact_utils
from crams_contact import models as contact_models
from crams.utils.role import AbstractCramsRoleUtils
from crams.extension.crams_aspects import CramsAspect, CRAMS_ASPECT_DICT


class EmptySerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CramsAspectSerializer:
    @classmethod
    def build_aspect_param_dict(cls, **kwargs):
        # return input parameters as a dict
        return kwargs
    
    @classmethod
    def get_method_aspect(cls, method_name):
        if cls not in CRAMS_ASPECT_DICT:
            return
        sz_aspect_obj = CRAMS_ASPECT_DICT.get(cls)
        if not isinstance(sz_aspect_obj, CramsAspect):
            raise exceptions.ValidationError('Crams Aspect for {} is not of type CramsAspect'.format(method_name))
        return sz_aspect_obj

    @classmethod
    def run_pre_aspect_for_method(cls, method_name, param_dict):
        sz_aspect_obj = cls.get_method_aspect(method_name)
        if not sz_aspect_obj:
            return
        if method_name not in sz_aspect_obj.pre_method_dict:
            return

        fn_list = sz_aspect_obj.pre_method_dict.get(method_name)
        for fn in fn_list:
            fn(cls, param_dict)

    @classmethod
    def run_post_aspect_for_method(cls, method_name, param_dict):
        sz_aspect_obj = cls.get_method_aspect(method_name)
        if not sz_aspect_obj:
            return
        if method_name not in sz_aspect_obj.post_method_dict:
            return

        fn_list = sz_aspect_obj.post_method_dict.get(method_name)
        for fn in fn_list:
            fn(cls, param_dict)


class CramsAPIActionStateModelSerializer(serializers.ModelSerializer, CramsAspectSerializer):
    """class ActionStateModelSerializer."""

    def __init__(self, instance=None, data=None, **kwargs):
        # No need to call this method, automatically called when serializer is intialised.
        if data:
            kwargs["data"] = data
        super().__init__(instance=instance, **kwargs)

        self.pp = pprint.PrettyPrinter(indent=4)  # For Debug
        self.cramsActionState = action_state.CramsAPIActionState(self)
        if self.cramsActionState.error_message:
            msg = 'ActionStateModelSerializer: ' + self.cramsActionState.error_message
            raise exceptions.ValidationError(msg)

        self.contact = contact_utils.fetch_user_contact_if_exists(self.get_current_user())

    def pprint(self, obj):
        self.pp.pprint(obj)

    def _setActionState(self):
        if not hasattr(self, 'cramsActionState'):
            self.cramsActionState = action_state.CramsAPIActionState(self)
            if self.cramsActionState.error_message:
                raise exceptions.ValidationError(
                    'ActionStateModelSerializer: ' +
                    self.cramsActionState.error_message)

    def get_current_user(self):
        user_obj = None
        if hasattr(self, 'cramsActionState'):
            user_obj = self.cramsActionState.rest_request.user
        if not user_obj:
            user_obj, _ = rest_utils.get_current_user_from_context(self)
        return user_obj

    def to_representation(self, instance):
        return super(CramsAPIActionStateModelSerializer, self).to_representation(instance)

    @classmethod
    def project_contact_has_readonly_access(cls, project, contact, erbs=None):
        # get erbs to check admin
        try:
            if erbs:
                if cls._is_admin(contact, erbs):
                    return False
            else:
                if project.requests.exists():
                    erbs = project.requests.first().e_research_system
                    if cls._is_admin(contact, erbs):
                        return False
        except:
            pass

        qs = project.project_contacts
        if qs and qs.filter(contact=contact,
                            contact_role__read_only=True).exists():
            return True
        return False

    def get_provision_roles_for_user(self, e_research_body_obj=None):
        fn = contact_utils.fetch_erb_userroles_with_provision_privileges
        return fn(self.get_current_user(), e_research_body_obj)

    def get_erbs_user_can_provision(self, e_research_body_obj=None):
        user_erb_roles = self.get_provision_roles_for_user(e_research_body_obj)
        erb_set = set()
        for erb_role in user_erb_roles:
            erb_set.add(erb_role.role_erb)
        return list(erb_set)

    def get_current_user_crams_token(self):
        return AbstractCramsRoleUtils.fetch_cramstoken_roles_dict(self.get_current_user())

    @staticmethod
    def _is_admin(user_contact, erbs):
        # check if user is a erb admin
        erb_admin_contacts = contact_models.CramsERBUserRoles.objects.filter(
            role_erb=erbs.e_research_body, contact=user_contact)

        # if user is an erb admin overrides the erbs admin
        for erb_admin_contact in erb_admin_contacts:
            if erb_admin_contact.is_erb_admin:
                return True

        # check if user is a erbs admin
        if erb_admin_contacts:
            if len(erb_admin_contacts) == 1:
                erb_admin_contact = erb_admin_contacts.first()
            else:
                # Fatal error users should have one or none CramsERBUserRole
                raise exceptions.ParseError(
                    'User has more than one CramsERBUserRole')

            # if user is an erb admin overrides the erbs admin
            if erb_admin_contact.is_erb_admin:
                return True

            # check user erbs admin matches with current erbs
            for admin_erbs in erb_admin_contact.admin_erb_systems.all():
                if admin_erbs == erbs:
                    return True

        return False
