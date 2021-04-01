# coding=utf-8
"""

"""
from crams.constants import api
from crams.models import ProvisionDetails
from crams.serializers.provision_details_serializer import AbstractProvisionDetailsSerializer


class CollectionProvisionDetailsSerializer(AbstractProvisionDetailsSerializer):
    """
    ==> from d3_prod crams.api.v1.serializers.utilitySerializers
    """
    """class ProvisionDetailsSerializer."""
    class Meta(object):
        model = ProvisionDetails
        fields = ('id', 'status', 'message')

    def validate(self, data):
        """validate.

        :param data:
        :return validated_data:
        """
        self.override_data = dict()
        if self.context:
            self.override_data = self.context.get(api.OVERRIDE_READONLY_DATA, None)
        return data

    def _get_new_provision_status(self, existing_status):

        if existing_status == ProvisionDetails.PROVISIONED:
            key = api.DO_NOT_OVERRIDE_PROVISION_DETAILS
            if self.override_data and self.override_data.get(key, False):
                pass
            else:
                return ProvisionDetails.POST_PROVISION_UPDATE

        return existing_status
