from rest_framework import serializers, exceptions
from django.utils import timezone

from crams.serializers import model_serializers
from crams.serializers.lookup_serializers import EResearchBodyIDKeySerializer
from crams import models as crams_models
from crams.utils import date_utils
from crams_contact import models as contact_models
from crams_contact.serializers import base_contact_serializer
from crams_software.config.software_config import ERB_Software_Email_fn_dict
from crams_software.config.software_config import get_erb_contact_id_key
from crams_software.config.software_config import get_erb_software_group_id_key
from crams_software.config.software_config import get_email_processing_fn
from crams_software import models as software_models


class ClusterLookupSerializer(model_serializers.ModelLookupSerializer):
    id = serializers.IntegerField(required=False)

    name = serializers.CharField(required=False)

    class Meta(object):
        model = crams_models.EResearchBodySystem
        fields = ['id', 'name']
        pk_fields = ['name']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        self.verify_field_value('name', attrs)
        self.verify_field_value('value', attrs)
        return self.instance or attrs


class TypeLookupSerializer(model_serializers.ModelLookupSerializer):
    id = serializers.IntegerField(required=False)

    type = serializers.CharField(required=False)

    class Meta(object):
        model = software_models.SoftwareLicenseType
        fields = ['id', 'type']
        pk_fields = ['type']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        self.verify_field_value('type', attrs)
        return self.instance or attrs


class CategoryLookupSerializer(model_serializers.ModelLookupSerializer):
    id = serializers.IntegerField(required=False)

    category = serializers.CharField(required=False)

    class Meta(object):
        model = software_models.SoftwareProductCategory
        fields = ['id', 'category']
        pk_fields = ['category']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        self.verify_field_value('category', attrs)
        return self.instance or attrs


class SoftwareProductMetaDataSz(model_serializers.UpdateModelLookupSerializer):
    id = serializers.IntegerField(required=False)

    name = EResearchBodyIDKeySerializer(
        required=False)

    value = serializers.CharField(required=False)

    class Meta(object):
        model = software_models.SoftwareProductMetaData
        fields = ['id', 'name', 'value']
        required_at_save = ['name', 'value']

    @classmethod
    def validate_name(cls, attrs):
        if isinstance(attrs, crams_models.EResearchBodyIDKey):
            return attrs

        key = attrs.get('key')
        e_research_body = attrs.get('e_research_body')
        msg = 'Key does not exist for {} / {}'
        try:
            return crams_models.EResearchBodyIDKey.objects.get(**attrs)
        except crams_models.EResearchBodyIDKey.DoesNotExist:
            raise exceptions(msg.format(key, e_research_body))

    def validate(self, data):
        data = super().validate(data)
        # cannot change ID Key on update
        self.verify_field_value('name', data)
        # serializer updatable, so do not return instance
        return data


class PosixIdProvisionDetail(model_serializers.ReadOnlyModelSerializer):
    posix_id = serializers.SerializerMethodField()

    email = serializers.SerializerMethodField()

    is_provisioned = serializers.SerializerMethodField()

    class Meta(object):
        model = software_models.ContactSoftwareLicense
        fields = ['posix_id', 'is_provisioned']

    @classmethod
    def get_posix_id(cls, contact_software_license_obj):
        erb = contact_software_license_obj.license.software.e_research_body
        key = get_erb_contact_id_key(erb.name)
        if not key:
            msg = 'Contact Key param not configured'
            raise exceptions.ValidationError(msg)
        sys = crams_models.EResearchBodyIDKey.objects.get(
            key=key, e_research_body=erb)

        identifier_qs = contact_software_license_obj.contact.system_identifiers
        if identifier_qs.exists():
            posix_qs = identifier_qs.filter(system=sys, prev_id__isnull=True)
            if posix_qs.exists():
                return posix_qs.first().identifier

        return None

    @classmethod
    def get_email(cls, contact_software_license_obj):
        return contact_software_license_obj.contact.email

    @classmethod
    def get_is_provisioned(cls, contact_software_license_obj):
        return contact_software_license_obj.provision_details is not None


class SoftwareProvisionDetailSerializer(model_serializers.
                                        ReadOnlyModelSerializer):
    group_id = serializers.SerializerMethodField()

    is_provisioned = serializers.SerializerMethodField()

    class Meta(object):
        model = software_models.SoftwareProduct
        fields = ['name', 'group_id', 'is_provisioned']

    @classmethod
    def get_is_provisioned(cls, software_product_obj):
        return software_product_obj.provision_details is not None

    @classmethod
    def get_group_id(cls, software_product_obj):
        erb = software_product_obj.e_research_body
        key = get_erb_software_group_id_key(erb.name)
        if not key:
            msg = 'Software Group Id Key param not configured'
            raise exceptions.ValidationError(msg)
        name_key = crams_models.EResearchBodyIDKey.objects.get(
            key=key, e_research_body=erb)
        qs = software_product_obj.metadata.filter(name=name_key)
        if qs.exists():
            return qs.first().value

        # msg = 'Group Id not defined for software {}'
        # raise exceptions.ValidationError(msg.format(software_product_obj))
        return None


class UserSoftwareProvisionSerializer(model_serializers.
                                      ReadOnlyModelSerializer):
    software = serializers.SerializerMethodField()

    user_ids = serializers.SerializerMethodField()

    # ListField(child=PosixIdProvisionDetail())

    class Meta(object):
        model = software_models.SoftwareProduct
        fields = ['software', 'user_ids']

    @classmethod
    def get_software(cls, sp_obj):
        return SoftwareProvisionDetailSerializer(sp_obj).data

    @classmethod
    def get_user_ids(cls, sp_obj):
        sl_qs = software_models.SoftwareLicense.objects.filter(
            software=sp_obj, end_date_ts__isnull=True)
        if not sl_qs.exists():
            return list()

        status = software_models.ContactSoftwareLicense.APPROVED
        user_license_qs = software_models.ContactSoftwareLicense.objects.filter(
            license__in=sl_qs, status=status)
        if not user_license_qs.exists():
            return list()

        return PosixIdProvisionDetail(user_license_qs, many=True).data


class SoftwareProductSerializer(model_serializers.UpdateModelLookupSerializer):
    id = serializers.IntegerField(required=False)

    category = CategoryLookupSerializer(required=False)

    metadata = SoftwareProductMetaDataSz(many=True, required=False)

    e_research_body = serializers.SlugRelatedField(
        'name', queryset=crams_models.EResearchBody.objects.all(),
        required=False)

    name = serializers.CharField(required=False)

    version = serializers.CharField(required=False, allow_null=True)

    description = serializers.CharField(
        style={'base_template': 'textarea.html'},
        required=False, allow_null=True)

    class Meta(object):
        model = software_models.SoftwareProduct
        fields = ['id', 'name', 'version', 'description', 'category',
                  'e_research_body', 'metadata']
        reverse_fk = [('metadata', 'software')]
        update_nested = ['metadata']
        required_at_save = ['category', 'e_research_body', 'name']

    def validate(self, data):
        data = super().validate(data)
        # cannot change e_research_body or name on update
        self.verify_field_value('e_research_body', data)
        # TODO ?? self.verify_field_value('name', data)
        # serializer updatable, so do not return instance
        return data


class UserSoftwareProductSerializer(SoftwareProductSerializer):
    user_status = serializers.SerializerMethodField()

    metadata = serializers.SerializerMethodField()

    class Meta(object):
        fields = ['id', 'name', 'version', 'description', 'category',
                  'e_research_body', 'metadata', 'user_status']
        required_at_save = []

    def create(self, validated_data):
        raise exceptions.ValidationError('Create not allowed')

    def update(self, instance, validated_data):
        raise exceptions.ValidationError('Update not allowed')

    @classmethod
    def get_metadata(cls, _):
        return None

    def get_user_status(self, software_product):
        current_contact = base_contact_serializer.get_serializer_user_contact(self)
        base_qs = software_product.licenses.filter(end_date_ts__isnull=True)
        if base_qs.exists():
            qs = base_qs.filter(user_licenses__contact=current_contact,
                                user_licenses__end_date_ts__isnull=True)
            if qs.exists():
                return qs.first().user_licenses.first().get_status_display()
            return 'Available'
        return 'Not Available'


class LicenseAgreementSz(model_serializers.UpdateModelLookupSerializer):
    id = serializers.IntegerField(required=False)

    version = serializers.CharField(required=False, allow_null=True)

    end_date_ts = serializers.DateTimeField(required=False, allow_null=True)

    is_academic = serializers.BooleanField(required=False)

    is_restricted = serializers.BooleanField(required=False)

    software = SoftwareProductSerializer(required=False)

    homepage = serializers.URLField(
        allow_blank=True, allow_null=True, max_length=200, required=False)

    type = TypeLookupSerializer(required=False)

    cluster = ClusterLookupSerializer(allow_null=True,
                                      many=True, required=False)

    start_date = serializers.DateField(required=False)

    license_text = serializers.CharField(
        style={'base_template': 'textarea.html'},
        allow_null=True, required=False)

    class Meta(object):
        model = software_models.SoftwareLicense
        fields = ['id', 'version', 'end_date_ts', 'is_academic', 'start_date',
                  'software', 'homepage', 'type', 'cluster', 'is_restricted',
                  'license_text']
        related_fk = ['software']
        update_nested = ['software']
        many_to_many = ['cluster']
        required_at_save = ['software', 'type', 'start_date']

    def validate(self, data):
        data = super().validate(data)
        # cannot change software on update
        # TODO self.verify_field_value('software', data)
        # serializer updatable, so do not return instance
        return data


class UserLicenseAgreementListSerializer(LicenseAgreementSz):
    contact_license = serializers.SerializerMethodField()

    class Meta(object):
        model = software_models.SoftwareLicense
        fields = ['id', 'version', 'end_date_ts', 'is_academic', 'start_date',
                  'software', 'homepage', 'type', 'cluster', 'is_restricted',
                  'license_text', 'contact_license']

    def get_relevant_contact(self):
        return base_contact_serializer.get_serializer_user_contact(self)

    def get_contact_license(self, softwarelicense_obj):
        contact = self.get_relevant_contact()
        base_qs = softwarelicense_obj.user_licenses
        if base_qs.exists():
            qs = base_qs.filter(contact=contact, end_date_ts__isnull=True)
            if qs.exists():
                return ReadOnlyContactLicenseChildSz(qs, many=True).data
        return None

    def create(self, validated_data):
        return exceptions.ValidationError('Create not allowed')

    def update(self, instance, validated_data):
        return exceptions.ValidationError('Update not allowed')


class ReadOnlyContactLicenseChildSz(model_serializers.ModelLookupSerializer):
    id = serializers.IntegerField(required=False)

    contact = serializers.SerializerMethodField()

    status = serializers.CharField(
        source='get_status_display', read_only=True, required=False)

    notes = serializers.CharField(style={'base_template': 'textarea.html'},
                                  allow_null=True, required=False)

    accepted_ts = serializers.DateTimeField(read_only=True, required=False)

    class Meta(object):
        model = software_models.ContactSoftwareLicense
        fields = ['id', 'contact', 'status', 'notes', 'accepted_ts']

    @classmethod
    def get_contact(cls, contact_license):
        contact = contact_license.contact
        return {
            'id': contact.id,
            'name': contact.get_full_name(),
            'email': contact.email
        }


class ContactLicenseAgreementSz(model_serializers.UpdateModelLookupSerializer,
                                ReadOnlyContactLicenseChildSz):
    license = LicenseAgreementSz(required=False)

    class Meta(object):
        model = software_models.ContactSoftwareLicense
        fields = ['id', 'contact', 'status', 'license',
                  'notes', 'accepted_ts']
        read_only_fields = ['accepted_ts', 'status']
        required_at_save = ['license']
        related_fk = ['license']

    def get_relevant_contact(self):
        return base_contact_serializer.get_serializer_user_contact(self)

    def create(self, validated_data):
        validated_data['contact'] = self.get_relevant_contact()
        validated_data['accepted_ts'] = date_utils.get_current_time_for_app_tz()
        validated_data['status'] = software_models.ContactSoftwareLicense.REQUEST_ACCESS
        new_csl = super().create(validated_data)

        # check if software has been expired
        # if expired can't allow user to apply
        expiry_date = validated_data["license"].end_date_ts
        if expiry_date:
            if timezone.now() > expiry_date:
                raise exceptions.ParseError(
                    'Software Product License has expired')

        # if license is not restricted automatically approve
        if not new_csl.license.is_restricted:
            new_csl.status = software_models.ContactSoftwareLicense.APPROVED
            new_csl.save()

        # fetch erbs
        erb = new_csl.license.software.e_research_body

        # send notification after request is made
        email_processing_fn = get_email_processing_fn(ERB_Software_Email_fn_dict, erb)
        if email_processing_fn:
            email_processing_fn(new_csl)
        return new_csl

    def validate(self, data):
        data = super().validate(data)
        # serializer updatable, so do not return instance
        return data

    def status_change_common(self, status_change_callback_fn):
        if not self.instance:
            msg = 'Instance not found, cannot update status'
            raise exceptions.ValidationError(msg)
        status_change_callback_fn(self.instance)
        self.instance.save()

        # fetch erbs
        erb = self.instance.license.software.e_research_body

        # send notification when status changed
        email_processing_fn = get_email_processing_fn(ERB_Software_Email_fn_dict, erb)
        if email_processing_fn:
            email_processing_fn(self.instance)

        return self.data

    def accept_user_license(self):
        def callback_fn(obj):
            if not obj.status == obj.REQUEST_ACCESS:
                msg = 'Cannot approve software request currently in status {}'
                raise exceptions.ValidationError(
                    msg.format(obj.get_status_display()))
            obj.status = obj.APPROVED
            obj.save()

        return self.status_change_common(callback_fn)

    def decline_user_license(self):
        def callback_fn(obj):
            if not obj.status == obj.REQUEST_ACCESS:
                msg = 'Cannot decline software request currently in status {}'
                raise exceptions.ValidationError(
                    msg.format(obj.get_status_display()))
            obj.status = obj.DECLINED
            obj.save()

        return self.status_change_common(callback_fn)


class ContactSerializer(model_serializers.ModelLookupSerializer):
    email = serializers.EmailField()
    posix_id = serializers.SerializerMethodField()

    class Meta(object):
        model = contact_models.Contact
        fields = ['email', 'posix_id']
        pk_fields = ['email']

    def get_posix_id(self, obj):
        erb = self.context.get("erb")
        erb_ids = crams_models.EResearchContactIdentifier.objects.filter(
            contact=obj,
            system__e_research_body=erb)

        posix_ids = list()
        for erb_id in erb_ids:
            posix_ids.append(erb_id.identifier)

        return posix_ids
