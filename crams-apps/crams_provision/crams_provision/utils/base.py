from rest_framework import exceptions
from rest_framework import serializers
from crams import models
from crams.utils.provision_detail_utils import ProvisionDetailUtils


class BaseProvisionUtils(serializers.Serializer):
    def __init__(self):
        pass

    @classmethod
    def get_build_provisioned(cls, obj, current_user):
        default_status = models.ProvisionDetails.SENT
        if not obj.provision_details:
            pd = models.ProvisionDetails(status=default_status, created_by=current_user)
            pd.save()
            obj.provision_details = pd
            obj.save()

        return ProvisionDetailUtils.get_provisioned(obj)

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
