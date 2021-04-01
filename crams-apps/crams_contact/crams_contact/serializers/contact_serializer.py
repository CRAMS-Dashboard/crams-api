# coding=utf-8
"""
contact Serializers
"""
import logging

from crams.serializers import model_serializers
from crams.utils import role
from crams_log.constants import log_actions
from crams_log.models import CramsLog
from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator

from crams_contact import models as contact_models
from crams_contact.serializers import lookup_serializers, base_contact_serializer
from crams_contact.serializers.crams_role_init import CramsRoleInitUtils, CramsRoleInitMetaClass
from crams_contact.serializers.role_free_contact_serializer import RoleFreeContactDetailsLookupSerializer
from crams_contact.serializers.role_free_contact_serializer import RoleFreeContactSerializer
from crams_contact.serializers.contact_id_sz import ContactIDSerializer


LOG = logging.getLogger(__name__)


class ContactDetailSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=True)
    type = serializers.ChoiceField(choices=contact_models.ContactDetail.TYPE_CHOICES)
    restricted = serializers.BooleanField()

    class Meta(object):
        model = contact_models.ContactDetail


class CramsContactLookupSerializer(model_serializers.ModelLookupSerializer):
    """class Contact Lookup Serializer"""
    id = serializers.IntegerField(required=False)

    given_name = serializers.CharField(required=False)

    surname = serializers.CharField(required=False)

    email = serializers.EmailField(required=False)

    class Meta(object):
        """metaclass."""
        model = contact_models.Contact
        fields = ('id', 'given_name', 'surname', 'email')
        read_only_fields = ('given_name', 'surname', 'email')

    def validate(self, attrs):
        super().validate(attrs)
        self.verify_field_value('email', attrs, ignore_case=True)
        return self.instance or attrs


class CramsContactDetailsLookupSerializer(RoleFreeContactDetailsLookupSerializer,
                                          CramsRoleInitUtils, metaclass=CramsRoleInitMetaClass):
    email = serializers.EmailField(validators=[])

    phone = serializers.SerializerMethodField()

    organisation = lookup_serializers.OrganisationLookupSerializer(
        many=False, required=False, allow_null=True)

    contact_details = serializers.SerializerMethodField()

    contact_ids = serializers.SerializerMethodField()

    class Meta(object):
        model = contact_models.Contact
        fields = ('id', 'title', 'given_name', 'surname', 'email', 'phone',
                  'organisation', 'orcid', 'scopusid', 'contact_details',
                  'contact_ids', 'latest_contact')
        read_only_fields = ('title', 'given_name', 'surname', 'orcid',
                            'scopusid', 'phone', 'organisation',
                            'contact_details', 'id', 'latest_contact')
        pk_fields = ['email']

    def get_contact_ids(self, contact):
        if not contact:
            return list()
        self.role_init()
        if not contact == self.contact:
            if not self.user_erb_set:
                return list()
        if hasattr(contact, 'system_identifiers'):
            qs = contact.system_identifiers
            return ContactIDSerializer(qs, many=True).data

    def get_phone(self, contact):
        self.role_init()
        if self.contact == contact or self.user_erb_set:
            return super().get_phone(contact)

        # TODO review phone number visibility
        return super().get_phone(contact)

    def get_contact_details(self, contact):
        self.role_init()
        if self.contact == contact or self.user_erb_set:
            return super().get_contact_details(contact)

    def validate(self, attrs):
        if hasattr(self, 'initial_data'):
            print('CramsContactDetailsLookupSerializer', self.initial_data)
        else:
            print('CramsContactDetailsLookupSerializer inst', self.instance)
        return super().validate(attrs)


class CramsContactSerializer(RoleFreeContactSerializer,
                             CramsRoleInitUtils, metaclass=CramsRoleInitMetaClass):
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

    def validate(self, data):
        current_user = self.get_current_user()
        if self.instance:
            if not current_user:
                user_msg = 'current user cannot be determined, update not permitted'
                raise exceptions.ValidationError(user_msg)

            contact_emails = self.get_related_emails(self.instance)
            if self.format_email(current_user.email) not in contact_emails:
                msg = 'Admin role required to update other Contact details'
                if not role.AbstractCramsRoleUtils.is_user_erb_admin(current_user):
                    raise exceptions.ValidationError(msg)

        return super().validate(data)


"""
from crams.models import User
qs = User.objects.all()
user_obj = qs.first()
from crams_contact.serializers import contact_serializer
sz_class = contact_serializer.CramsContactDetailsLookupSerializer
c = sz_class.fetch_or_create_given_user_as_contact(user_obj)

"""


class ContactSerializer(base_contact_serializer.BaseContactSerializer):
    email = serializers.EmailField(
        required=True, validators=[
            UniqueValidator(queryset=contact_models.Contact.objects.all())])

    contact_ids = serializers.SerializerMethodField()

    organisation = lookup_serializers.OrganisationLookupSerializer(
        many=False, required=False, allow_null=True)

    last_login = serializers.SerializerMethodField()

    class Meta(object):
        model = contact_models.Contact
        fields = ['id', 'title', 'given_name', 'surname', 'email', 'phone',
                  'organisation', 'orcid', 'scopusid', 'contact_details',
                  'latest_contact', 'contact_ids', 'last_login']
        read_only_fields = []

    @classmethod
    def get_last_login(cls, obj):
        qs = CramsLog.objects.filter(
            created_by__iexact=obj.email,
            action__action_type=log_actions.LOGIN).order_by('-creation_ts')

        # distinct get one of each site logged in
        sites = qs.order_by('type').values_list('type__name').distinct()
        results = []
        try:
            for site in sites:
                qs_sites = qs.filter(type__name=site[0])
                if qs_sites:
                    results.append({'site': qs_sites[0].type.name, 'date': qs_sites[0].creation_ts})
        except:
            return None

        return results

    @classmethod
    def add_related_entities(cls, contact, validated_data):
        RoleFreeContactSerializer.add_related_entities(contact, validated_data)

    def validate(self, data):
        self._setActionState()
        # the following fields are serializer method fields
        data['phone'] = self.initial_data.get('phone')

        contact_details = self.initial_data.get('contact_details')
        if contact_details:
            self.validate_contact_details(contact_details)
            data['contact_details'] = contact_details

        if self.cramsActionState.is_update_action:
            current_user = self.get_current_user()
            instance = self.cramsActionState.existing_instance
            if not role.AbstractCramsRoleUtils.is_user_erb_admin(current_user):
                contact_emails = self.get_related_emails(instance)
                msg = 'Admin role required to update other Contact details'
                if self.format_email(current_user.email) not in contact_emails:
                    raise exceptions.ValidationError(msg)

        if self.cramsActionState.is_create_action:
            latest_contact = data.get('latest_contact')
            if latest_contact:
                msg = 'historical Contact, edit current contact instead'
                raise exceptions.ValidationError(msg)

        return data

    @classmethod
    def setup_default_contact_detail(cls, parent_contact):
        return RoleFreeContactSerializer.setup_default_contact_detail(parent_contact=parent_contact)

    def create(self, validated_data):
        print(' in create proper')
        return RoleFreeContactSerializer.create(validated_data=validated_data)

    def update(self, instance, validated_data):
        return RoleFreeContactSerializer.update(instance, validated_data)
