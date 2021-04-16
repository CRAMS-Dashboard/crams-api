# coding=utf-8
"""

"""

from crams_storage.models import StorageProductProvisionId
from rest_framework import exceptions


def validate_current_use_return_provision_id(provision_id, sr_instance):
    """
    validate input provision id is not used for the same product as sr_instance in another current project
    :param provision_id: char
    :param sr_instance: storage_request instace where this provision id will be linked to
    :return:
    """
    if not provision_id:
        return
    msg = 'Provision Id {} in use by Project: {}'
    try:
        spp_obj = StorageProductProvisionId.objects.get(
            provision_id=provision_id,
            storage_product=sr_instance.storage_product)
        spp_in_use_qs = spp_obj.storage_requests.filter(
            request__current_request__isnull=True).exclude(
            pk=sr_instance.id)
        if spp_in_use_qs.exists():
            project = spp_in_use_qs.first().request.project
            raise exceptions.ValidationError(msg.format(
                provision_id, project.title))
    except StorageProductProvisionId.DoesNotExist:
        spp_obj = StorageProductProvisionId.objects.create(
            provision_id=provision_id,
            storage_product=sr_instance.storage_product)
    return spp_obj
