# coding=utf-8
"""

"""

from rest_framework.exceptions import ParseError, ValidationError
from crams.constants import api
from crams.models import ProvisionDetails
from crams.serializers.provision_details_serializer import AbstractProvisionDetailsSerializer


class AllocationProvisionDetailsSerializer(AbstractProvisionDetailsSerializer):
    """
    ==> from d3_prod crams.api.v1.serializers.utilitySerializers
    """
    """class AllocationProvisionDetailsSerializer."""
    def validate(self, data):
        """validate.

        :param data:
        :return validated_data:
        """
        self.override_data = dict()
        if self.context:
            self.override_data = self.context.get(api.OVERRIDE_READONLY_DATA, None)

        if data['status'] in ProvisionDetails.SET_OF_SENT:
            parentProductRequest = ''
            if self.existing:
                if self.existing.compute_requests:
                    parentProductRequest = self.existing.compute_requests
                elif self.existing.storage_requests:
                    parentProductRequest = self.existing.storage_requests
            raise ValidationError({'Product Request ':
                                   '{} cannot be updated while being \
                                   provisioned'
                                   .format(repr(parentProductRequest))})

        return data

    def _get_new_provision_status(self, existing_status):

        if existing_status == ProvisionDetails.PROVISIONED:
            key = api.DO_NOT_OVERRIDE_PROVISION_DETAILS
            if self.override_data and self.override_data.get(key, False):
                pass
            else:
                return ProvisionDetails.POST_PROVISION_UPDATE

        return existing_status
