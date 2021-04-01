import logging

# from django.conf import settings
from django.contrib import auth
from django.db import transaction
# from django.db.models import Q
from rest_framework import serializers, exceptions

# from crams.utils import lang_utils
# from crams.models import ProvisionDetails
from crams_contact.models import EResearchContactIdentifier
from crams_contact.serializers import contact_id_sz
from crams.utils.role import AbstractCramsRoleUtils
from crams_collection.utils import project_user_utils
from crams_provision.utils import base

LOG = logging.getLogger(__name__)
User = auth.get_user_model()


class ProvisionContactIDSerializer(contact_id_sz.ContactIDSerializer):

    provisioned = serializers.SerializerMethodField()

    class Meta(object):
        """meta Class."""

        model = EResearchContactIdentifier
        fields = ['id', 'identifier', 'system', 'provisioned']

    def get_provisioned(self, obj, current_user=None):
        if not current_user:
            current_user = self.get_current_user()
        return base.BaseProvisionUtils.get_build_provisioned(obj, current_user=current_user)

    def get_current_user(self):
        user, _ = project_user_utils.get_current_user_from_context(self)
        if not user:
            raise exceptions.ValidationError({
                'message': 'Unable to determine current user for api request'})
        return user

    @classmethod
    def update_contact_data_list(cls, id_key, contact_data_list):
        contact_id_obj_list = \
            contact_id_sz.ContactIDSerializer.update_contact_data_list(id_key, contact_data_list)

        return contact_id_obj_list

    def validate(self, data):
        validated_data = super().validate(data)

        msg_param = 'Contact Id'
        provisioned_status = self.initial_data.get('provisioned', False)
        is_clone = 'CLONE' in self.context
        is_admin = AbstractCramsRoleUtils.is_user_erb_admin(self.get_current_user())
        base_prov_cls = base.BaseProvisionUtils
        base_prov_cls.validate_provisioned(
            provisioned_status, self.instance, msg_param, is_clone, is_admin)
        if self.instance:
            identifier = validated_data.get('identifier')
            if identifier == self.instance.identifier and \
                    not provisioned_status and not is_clone and not is_admin:
                raise exceptions.ValidationError('No change to identifier')
            validated_data['provisioned'] = provisioned_status

        return validated_data

    @transaction.atomic
    def update(self, instance, validated_data):
        base_prov_cls = base.BaseProvisionUtils
        new_pd = base_prov_cls.build_new_provision_details(
            instance, validated_data, self.get_current_user())
        new_pd.save()
        validated_data['provision_details'] = new_pd

        new_instance = super().update(instance, validated_data)

        # # check if notifications are required to be sent
        # new_pd_status = None
        # if new_instance.provision_details:
        #     new_pd_status = new_instance.provision_details.status
        #
        # old_pd_status = None
        # if instance.provision_details:
        #     old_pd_status = instance.provision_details.status

        # if new_pd_status == ProvisionDetails.PROVISIONED and \
        #         not new_pd_status == old_pd_status:
        #     TODO self.process_notifications(new_instance)

        return new_instance

    # @classmethod
    # def process_notifications(cls, contact_id_obj):
    #     qs_filter = Q(system_key=contact_id_obj.system,
    #                   e_research_body=contact_id_obj.system.e_research_body,
    #                   request_status__code=REQUEST_STATUS_PROVISIONED)
    #     qs = NotificationTemplate.objects.filter(qs_filter)
    #     for n_template in qs.all():
    #         cls.process_notification_template(n_template, contact_id_obj)

    @classmethod
    def populate_email_dict(cls, contact_id_obj):
        return contact_id_obj

    # @classmethod
    # def process_notification_template(cls, template_obj, contact_id_obj):
    #     template = template_obj.template_file_path
    #
    #     mail_content = cls.populate_email_dict(contact_id_obj)
    #     erb_obj = contact_id_obj.system.e_research_body
    #     desc = contact_id_obj.contact.get_full_name()
    #     subject = erb_obj.name + ' Identifier Provisioned for ' + desc
    #
    #     try:
    #         fn = notification_utils.build_erb_notification_recipient_list
    #         contact = contact_id_obj.contact
    #         recipient_list = fn(erb_obj, template_obj, contact_obj=contact)
    #
    #         reply_to = eSYSTEM_REPLY_TO_EMAIL_MAP.get(
    #             lang_utils.strip_lower(erb_obj.name))
    #
    #         send_email_notification.delay(
    #             sender=reply_to,
    #             subject=subject,
    #             mail_content=mail_content,
    #             template_name=template,
    #             recipient_list=recipient_list,
    #             cc_list=None,
    #             bcc_list=None,
    #             reply_to=reply_to)
    #
    #     except Exception as e:
    #         error_message = '{} : Project - {}'.format(repr(e), desc)
    #         LOG.error(error_message)
    #         if settings.DEBUG:
    #             raise Exception(error_message)


class ProvisionedContactSystemIdentifiers(serializers.Serializer):
    system_identifiers = ProvisionContactIDSerializer(
        many=True, required=False)
    given_name = serializers.CharField(required=False)
    surname = serializers.CharField(required=False)
    email = serializers.EmailField()
    id = serializers.IntegerField(required=False)

    class Meta(object):
        fields = ['id', 'given_name', 'surname', 'email', 'system_identifiers']
        read_only_fields = ['first_name', 'last_name', 'id']
