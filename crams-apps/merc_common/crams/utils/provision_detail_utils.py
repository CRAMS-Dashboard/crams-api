# coding=utf-8
"""

"""

from rest_framework import exceptions

from crams import models


class ProvisionDetailUtils:
    def __init__(self):
        pass

    @classmethod
    def get_provisioned(cls, obj):
        p_details = obj.provision_details
        provisioned_list = [models.ProvisionDetails.PROVISIONED]
        return p_details and p_details.status in provisioned_list

    @classmethod
    def validate_provisioned(cls, provisioned_status, instance, msg_param,
                             is_clone=False, is_admin=False):

        if provisioned_status not in [True, False]:
            msg = 'provisioned value must be boolean, not {}'
            raise exceptions.ValidationError(
                msg.format(provisioned_status.__class__.__name__))

        if is_clone or is_admin:
            return

        msg = 'not sent for provisioning, hence cannot be update ' \
              'Provision status'
        if instance:
            pd = instance.provision_details
            if pd:
                if pd.status in models.ProvisionDetails.SET_OF_SENT:
                    msg = 'cannot be updated unless provision status ' \
                          'is set to true'
                    if provisioned_status:
                        return
                if pd.status == models.ProvisionDetails.PROVISIONED:
                    msg = 'is currently provisioned, cannot be updated'
        raise exceptions.ValidationError(msg_param + ' ' + msg)

    @classmethod
    def build_new_provision_details(
            cls, instance, validated_data, current_user):
        message = validated_data.get('message', None)

        status = models.ProvisionDetails.UNKNOWN
        # create copy of previous provision details
        if instance.provision_details:
            old_pd = instance.provision_details
            if not message:
                message = old_pd.message
            status = old_pd.status

        provisioned = validated_data.pop('provisioned')
        if provisioned:
            status = models.ProvisionDetails.PROVISIONED
            message = None

        return models.ProvisionDetails(
            status=status, message=message, created_by=current_user)

    @classmethod
    def get_sent_object(cls, message=None):
        status = models.ProvisionDetails.SENT
        return cls.build_object(status, message)

    @classmethod
    def validate_existing_details_obj(
            cls, existing_details_obj, expected_status_set):
        if not isinstance(existing_details_obj, models.ProvisionDetails):
            msg = 'Provision Details sent instance expected, got {}'.format(
                type(existing_details_obj))
            raise exceptions.ParseError(msg)

        if not existing_details_obj.id:
            msg = 'to validate, Provision Details must be an existing object'
            raise exceptions.ParseError(msg)

        status = existing_details_obj.status
        if status not in expected_status_set:
            msg = 'Provision Details status must be one of {} got {}'.format(
                expected_status_set, status)
            raise exceptions.ParseError(msg)

    @classmethod
    def get_post_provision_update_sent_object(
            cls, existing_details_obj, message=None):
        expected_set = set(models.ProvisionDetails.POST_PROVISION_UPDATE)
        cls.validate_existing_details_obj(existing_details_obj, expected_set)
        status = models.ProvisionDetails.POST_PROVISION_UPDATE_SENT
        return cls.build_object(status, message)

    @classmethod
    def get_post_provision_update_object(
            cls, existing_details_obj, message=None):
        cls.validate_existing_details_obj(
            existing_details_obj, set(models.ProvisionDetails.PROVISIONED))
        status = models.ProvisionDetails.POST_PROVISION_UPDATE
        return cls.build_object(status, message)

    @classmethod
    def get_provisioned_object(cls, provisioned_details_obj, message=None):
        cls.validate_existing_details_obj(
            provisioned_details_obj, models.ProvisionDetails.SET_OF_SENT)
        status = models.ProvisionDetails.PROVISIONED
        return cls.build_object(status, message)

    @classmethod
    def get_failed_object(cls, sent_details_obj, message):
        cls.validate_existing_details_obj(
            sent_details_obj, models.ProvisionDetails.SET_OF_SENT)
        status = models.ProvisionDetails.FAILED
        return cls.build_object(status, message)

    @classmethod
    def build_object(cls, status, message):
        # Do not save here, just leave it in memory
        return models.ProvisionDetails(status=status, message=message)

    @classmethod
    def update_or_get_new_provisiondetails_object(
            cls, provisionable_object, status_boolean):

        p_status = models.ProvisionDetails.SENT
        p_message = None
        if status_boolean:
            p_status = models.ProvisionDetails.PROVISIONED
            p_message = None

        existing_provision_detail = provisionable_object.provision_details
        if existing_provision_detail:
            if not status_boolean and existing_provision_detail.status \
                    == models.ProvisionDetails.PROVISIONED:
                msg = 'Cannot de-provision a provisioned identifier'
                raise exceptions.ValidationError(msg)
            existing_provision_detail.status = p_status
            existing_provision_detail.message = None
            # Do not save here, just leave it in memory
            return existing_provision_detail

        return cls.build_object(status=p_status, message=p_message)
