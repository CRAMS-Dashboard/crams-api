# coding=utf-8
"""
contact Serializers
"""
import logging

from django.contrib import auth
from django.db.models import Q
from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator

from crams.serializers import model_serializers
from crams_contact import models as contact_models
from crams_contact.config import contact_config
from crams_contact.serializers import lookup_serializers

LOG = logging.getLogger(__name__)
User = auth.get_user_model()


class RoleFreeContactDetailsLookupSerializer(model_serializers.ModelLookupSerializer):
    id = serializers.IntegerField(required=False)
    
    title = serializers.CharField(required=False, allow_null=True)

    given_name = serializers.CharField(required=False, allow_null=True)

    surname = serializers.CharField(required=False, allow_null=True)

    orcid = serializers.CharField(required=False, allow_null=True)

    scopusid = serializers.CharField(required=False, allow_null=True)

    email = serializers.EmailField(validators=[])

    phone = serializers.SerializerMethodField(required=False, allow_null=True)

    organisation = lookup_serializers.OrganisationLookupSerializer(
        many=False, required=False, allow_null=True)

    contact_details = serializers.SerializerMethodField()

    class Meta(object):
        model = contact_models.Contact
        fields = ('id', 'title', 'given_name', 'surname', 'email', 'phone',
                  'organisation', 'orcid', 'scopusid', 'contact_details', 'latest_contact')
        read_only_fields = ('title', 'given_name', 'surname', 'orcid',
                            'scopusid', 'phone', 'organisation',
                            'contact_details', 'id', 'latest_contact')
        pk_fields = ['email']

    def create(self, validated_data):
        raise exceptions.ParseError('Create not allowed ')

    def update(self, instance, validated_data):
        raise exceptions.ParseError('Update not allowed ')

    def __delete__(self, instance):
        raise exceptions.ParseError('Delete not allowed ')

    @classmethod
    def fetch_first_contact_obj(cls, validated_data):
        return cls.fetch_contacts(validated_data).first()

    @classmethod
    def fetch_contacts(cls, validated_data):
        email = validated_data.get('email')
        if email:
            qs_filter = Q(email__iexact=email) | Q(
                contact_details__email__iexact=email)
        else:
            pk = validated_data.get('id')
            qs_filter = Q(pk=pk)

        if not qs_filter:
            return contact_models.Contact.objects.none()
        return contact_models.Contact.objects.filter(qs_filter).distinct()

    @classmethod
    def search_contact_get_queryset(cls, pk=None, email=None):
        search_dict = dict()
        if pk:
            search_dict['id'] = pk
        if email:
            search_dict['email'] = email
        if search_dict:
            return cls.fetch_contacts(search_dict)
        return None

    @classmethod
    def get_details_queryset(cls, contact):
        qs = contact.contact_details
        return qs.filter(restricted=False).order_by('type')

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

    def get_phone(self, contact):
        def get_first_available_phone_number():
            if not contact.phone:
                for detail in self.get_details_queryset(contact):
                    phone = detail.phone
                    if phone:
                        return phone
            return contact.phone

        return get_first_available_phone_number()

    def get_contact_details(self, contact):
        ret_list = list()
        for detail in self.get_details_queryset(contact):
            detail_dict = dict()
            detail_dict['type'] = detail.get_type_display()
            detail_dict['phone'] = detail.phone
            detail_dict['email'] = detail.email
            ret_list.append(detail_dict)
        return ret_list

    @classmethod
    def get_related_emails(cls, contact_obj):
        if contact_obj:
            email_set = set()
            email_set.add(cls.format_email(contact_obj.email))
            for detail in contact_obj.contact_details.all():
                if detail.email:
                    email_set.add(cls.format_email(detail.email))
            return list(email_set)
        return list()

    @classmethod
    def format_email(cls, email_in):
        if email_in:
            return email_in.strip().lower()
        return None

    def validate(self, attrs):
        print('RoleFreeContactDetailsLookupSerializer', attrs)
        super().validate(attrs)
        self.verify_field_value('email', attrs, ignore_case=True)
        print('returning ', self.instance)
        return self.instance or attrs


class RoleFreeContactSerializer(RoleFreeContactDetailsLookupSerializer):
    email = serializers.EmailField(
        required=True, validators=[
            UniqueValidator(queryset=contact_models.Contact.objects.all())])

    organisation = lookup_serializers.OrganisationLookupSerializer(
        many=False, required=False, allow_null=True)

    class Meta(object):
        model = contact_models.Contact
        fields = ('id', 'title', 'given_name', 'surname', 'email', 'phone',
                  'organisation', 'orcid', 'scopusid', 'contact_details',
                  'latest_contact', 'contact_ids')
        read_only_fields = ()
        pk_fields = ['email']

    @classmethod
    def add_related_entities(cls, contact, validated_data):
        related_tables_map = {
            'contact_details': contact_models.ContactDetail
        }

        for key, model in related_tables_map.items():
            data = validated_data.get(key)
            if data:
                for instance_data in data:
                    instance = model(**instance_data)
                    instance.parent_contact = contact
                    instance.save()

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
        # the following fields are serializer method fields
        data['phone'] = self.initial_data.get('phone')

        contact_details = self.initial_data.get('contact_details')
        if contact_details:
            self.validate_contact_details(contact_details)
            data['contact_details'] = contact_details

        latest_contact = data.get('latest_contact')
        if latest_contact:
            msg = 'historical Contact, edit current contact instead'
            raise exceptions.ValidationError(msg)

        return data

    @classmethod
    def setup_default_contact_detail(cls, parent_contact):
        contact_models.ContactDetail(
            type=contact_models.ContactDetail.BUSINESS,
            parent_contact=parent_contact,
            phone=parent_contact.phone,
            email=parent_contact.email).save()

    @classmethod
    def create(cls, validated_data):
        try:
            contact = cls.fetch_first_contact_obj(validated_data)
            if contact:
                email = validated_data.get('email')
                msg = 'Contact exists for email: ' + email
                raise exceptions.ParseError(msg)
        except contact_models.Contact.DoesNotExist:
            pass

        related_tables_data = dict()
        contact_details = validated_data.pop('contact_details', None)

        contact = contact_models.Contact.objects.create(**validated_data)
        if not contact_details:
            cls.setup_default_contact_detail(contact)
        else:
            related_tables_data['contact_details'] = contact_details
            cls.add_related_entities(contact, related_tables_data)

        # create/update default ERB Body Contact Ids for this contact
        contact_config.update_erb_contact_ids_for_key(contact)

        return contact

    @classmethod
    def update(cls, instance, validated_data):
        if 'title' in validated_data:
            instance.title = validated_data.get('title')
        if 'surname' in validated_data:
            instance.surname = validated_data.get('surname')
        if 'given_name' in validated_data:
            instance.given_name = validated_data.get('given_name')
        if 'phone' in validated_data:
            instance.phone = validated_data.get('phone')
        if 'orcid' in validated_data:
            instance.orcid = validated_data.get('orcid')
        if 'scopusid' in validated_data:
            instance.scopusid = validated_data.get('scopusid')
        if 'email' in validated_data:
            instance.email = validated_data.get('email')
        if 'organisation' in validated_data:
            instance.organisation = validated_data.get('organisation')

        instance.save()

        contact_details = validated_data.get('contact_details')
        if contact_details:
            for detail in contact_details:
                email = detail.get('email')
                phone = detail.get('phone')
                type_str = detail.get('type')
                if not type_str:
                    msg = 'Contact Detail Type required'
                    raise exceptions.ValidationError(msg)

                contact_type = contact_models.ContactDetail.get_choice_value(type_str)
                if not contact_type:
                    msg = 'Contact Detail Type {} not valid'.format(type_str)
                    raise exceptions.ValidationError(msg)

                try:
                    detail_obj = \
                        instance.contact_details.get(type=contact_type)
                    detail_obj.email = email
                    detail_obj.phone = phone
                    detail_obj.save()
                except contact_models.ContactDetail.DoesNotExist:
                    contact_models.ContactDetail(
                        type=contact_type, parent_contact=instance,
                        phone=phone, email=email).save()
                except contact_models.ContactDetail.MultipleObjectsReturned:
                    msg = \
                        'Data error, multiple details exists for contact type'
                    raise exceptions.ValidationError(msg.format(type_str))

        if not instance.contact_details.exists():
            cls.setup_default_contact_detail(instance)

        # create/update default ERB Body Contact Ids for this contact
        contact_config.update_erb_contact_ids_for_key(instance)

        return instance
