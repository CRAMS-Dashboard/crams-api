# coding=utf-8
"""

"""
import logging
from rest_framework import serializers
from crams.models import User
from crams.utils import rest_utils
from crams.utils.role import AbstractCramsRoleUtils
from rest_framework import exceptions

from crams_contact import models as contact_models

LOG = logging.getLogger(__name__)


class CramsRoleInitMetaClass(serializers.SerializerMetaclass):
    def __init__(cls, class_name, superclasses, attribute_dict):
        super().__init__(class_name, superclasses, attribute_dict)
        cls.current_user = None
        cls.contact = None
        cls.user_erb_set = set()
        cls.user_erb_system_list = list()

    # def __new__(mcs, class_name, bases, dct):
    #     new_class = super(CramsRoleInitMetaClass, mcs).__new__(mcs, class_name, bases, dct)
    #     setattr(new_class, mcs.role_init.__name__, mcs.role_init)
    #     setattr(new_class, mcs.get_current_user.__name__, mcs.get_current_user)
    #     setattr(new_class, mcs.fetch_or_create_given_user_as_contact.__name__,
    #             mcs.fetch_or_create_given_user_as_contact)
    #     return new_class


class CramsRoleInitUtils:
    # Note: The init below is not called by the Model Serializer
    #  - so we use the above CramsRoleInitMetaClass to initialize the variables
    #  - the init below is dummy and never used when inherited together with Model Serializer
    def __init__(self):
        self.current_user = None
        self.contact = None
        self.user_erb_set = set()
        self.user_erb_system_list = list()

    def role_init(self):
        if not self.contact:
            user_obj = self.get_current_user()
            if user_obj:
                self.contact = self.fetch_or_create_given_user_as_contact(user_obj)
                self.user_erb_system_list = AbstractCramsRoleUtils.get_authorised_e_research_system_list(user_obj)
                for erb_system in self.user_erb_system_list:
                    self.user_erb_set.add(erb_system.e_research_body)

    @classmethod
    def fetch_or_create_given_user_as_contact(cls, user_obj):
        if not isinstance(user_obj, User):
            msg = 'Contact fetch expects User object, got'
            raise exceptions.ValidationError(msg + type(user_obj))
        try:
            contact = contact_models.Contact.objects.get(email=user_obj.email)
        except contact_models.Contact.DoesNotExist:
            contact_data = {
                'email': user_obj.email,
                'given_name': user_obj.first_name,
                'surname': user_obj.last_name
            }
            contact = contact_models.Contact(**contact_data)
            contact.save()
        return contact

    def get_current_user(self):
        if not self.current_user:
            self.current_user, context = rest_utils.get_current_user_from_context(self)
        return self.current_user
