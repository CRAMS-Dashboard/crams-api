# coding=utf-8
"""
read only contact Serializer
"""
import logging

from django.db.models import Q
from rest_framework import serializers, exceptions

from crams.utils import rest_utils
from crams.models import User
from crams_contact import models as contact_models
from crams_contact.serializers import contact_id_sz
from crams_contact.serializers import lookup_serializers
from crams_contact.serializers.role_free_contact_serializer import RoleFreeContactSerializer
from crams_contact.serializers.util_sz import CramsAPIActionStateModelSerializer
from crams_contact.utils import contact_utils

LOG = logging.getLogger(__name__)


def get_serializer_user_contact(serializer_self):
    user, context = rest_utils.get_current_user_from_context(serializer_self)
    if user:
        return BaseContactSerializer(context=context). \
            fetch_or_create_given_user_as_contact(user)

    msg = '"context" object not found, required to identify current user.'
    raise exceptions.ValidationError({'message': msg})


class BaseContactSerializer(CramsAPIActionStateModelSerializer):
    """
    A read-only version of contact with limited ability to add new contact for search purposes
    - allows creation of a new contact with email value only.
    """
    email = serializers.EmailField(validators=[])

    phone = serializers.SerializerMethodField()

    organisation = lookup_serializers.OrganisationLookupSerializer(
        many=False, required=False, allow_null=True)

    contact_details = serializers.SerializerMethodField()

    class Meta(object):
        model = contact_models.Contact
        fields = ['id', 'title', 'given_name', 'surname', 'email', 'phone',
                  'organisation', 'orcid', 'scopusid', 'contact_details',
                  'latest_contact']
        read_only_fields = ['title', 'given_name', 'surname', 'orcid',
                            'scopusid', 'phone', 'organisation',
                            'contact_details', 'id', 'latest_contact']

    def update(self, instance, validated_data):
        raise exceptions.ParseError('Update not allowed ')

    def __delete__(self, instance):
        raise exceptions.ParseError('Delete not allowed ')

    def create(self, validated_data):
        print('in Base')
        raise exceptions.ParseError('Create not allowed ')

    @classmethod
    def get_details_queryset(cls, contact):
        qs = contact.contact_details
        return qs.filter(restricted=False).order_by('type')

    def intialise(self):
        if not hasattr(self, 'self_contact'):
            self.self_contact = get_serializer_user_contact(self)

            self.user_erb_system_list = \
                contact_utils.fetch_related_user_erb_system_list(self)

            self.user_erb_set = set()
            for erb_system in self.user_erb_system_list:
                self.user_erb_set.add(erb_system.e_research_body)

    @classmethod
    def get_email(cls, contact):
        if not contact.email:
            for detail in cls.get_details_queryset(contact):
                if detail.email:
                    return detail.email
        return contact.email

    @classmethod
    def get_organisation(cls, contact):
        if contact.organisation:
            return contact.organisation
        else:
            return None

    @classmethod
    def search_contact_get_queryset(cls, pk=None, email=None):
        search_dict = dict()
        if pk:
            search_dict['id'] = pk
        if email:
            search_dict['email'] = email
        if search_dict:
            return RoleFreeContactSerializer.fetch_contacts(search_dict)
        return None

    def get_contact_ids(self, contact_obj):
        self.intialise()
        if not contact_obj:
            return list()

        qs = contact_obj.system_identifiers
        if not contact_obj == self.self_contact:
            if not self.user_erb_set:
                return list()
            else:
                # if not self, should see only authorised erb identifiers
                filter_qs = Q(system__e_research_body__in=self.user_erb_set)
                qs = qs.filter(filter_qs)

        return contact_id_sz.ContactIDSerializer(qs, many=True).data

    def get_phone(self, contact):
        def get_first_available_phone_number():
            if not contact.phone:
                for detail in self.get_details_queryset(contact):
                    phone = detail.phone
                    if phone:
                        return phone
            return contact.phone

        self.intialise()
        if self.self_contact == contact or self.user_erb_set:
            return get_first_available_phone_number()

        # TODO review phone number visibility
        return get_first_available_phone_number()

    def get_contact_details(self, contact):
        self.intialise()
        if self.self_contact == contact or self.user_erb_set:
            ret_list = []
            for detail in self.get_details_queryset(contact):
                detail_dict = dict()
                detail_dict['type'] = detail.get_type_display()
                detail_dict['phone'] = detail.phone
                detail_dict['email'] = detail.email
                ret_list.append(detail_dict)
            return ret_list

    @classmethod
    def get_related_emails(cls, contact_obj):
        return RoleFreeContactSerializer.get_related_emails(contact_obj)

    @classmethod
    def format_email(cls, email_in):
        if email_in:
            return email_in.strip().lower()
        return None

    @classmethod
    def validate_email(cls, email):
        email = cls.format_email(email)
        if not email:
            msg = 'Email required, cannot resolve to None'
            raise exceptions.ValidationError(msg)
        return email

    @classmethod
    def validate_contact_details(cls, contact_details):
        if contact_details:
            for c_d in contact_details:
                c_d['email'] = cls.format_email(c_d.get('email'))
        return contact_details

    def validate(self, data):
        msg = 'email required to fetch contact data'
        email = data.get('email')
        try:
            if email:
                return contact_models.Contact.objects.get(email__iexact=email)
        except contact_models.Contact.DoesNotExist:
            msg = 'Contact not found for email ' + email
        except Exception as e:
            msg = str(e)

        raise exceptions.ValidationError(msg)

    def fetch_or_create_given_user_as_contact(self, user_obj):
        if not isinstance(user_obj, User):
            msg = 'Contact fetch expects User object, got'
            raise exceptions.ValidationError(msg + type(user_obj))

        contact_data = {
            'email': user_obj.email,
            'given_name': user_obj.first_name,
            'surname': user_obj.last_name
        }
        return self.get_or_create(contact_data)

    def get_or_create(self, validated_data):
        contact = None
        try:
            contact = RoleFreeContactSerializer.fetch_first_contact_obj(validated_data=validated_data)
        except contact_models.Contact.DoesNotExist:
            pass
        if not contact:
            contact = self.create(validated_data)
        return contact
