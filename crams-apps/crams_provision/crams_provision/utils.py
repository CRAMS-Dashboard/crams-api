# coding=utf-8
"""

"""
import copy
from rest_framework import exceptions
from crams import models as crams_models
from crams.common.utils import log_process


def validate_current_use_return_provision_id(provision_id, sr_instance):
    """
    validate input provision id is not used for the same product as sr_instance in another current project
    :param provision_id: char
    :param sr_instance: storage_request instace where this provision id will be linked to
    :return:
    """
    if not provision_id:
        return
    msg = 'Provision Id "{}" in use by Project: {}'
    try:
        spp_obj = crams_models.StorageProductProvisionId.objects.get(
            provision_id=provision_id,
            storage_product=sr_instance.storage_product)
        spp_in_use_qs = spp_obj.storage_requests.filter(
            request__current_request__isnull=True).exclude(
            pk=sr_instance.id)
        if spp_in_use_qs.exists():
            project = spp_in_use_qs.first().request.project
            raise exceptions.ValidationError(msg.format(
                provision_id, project.title))
    except crams_models.StorageProductProvisionId.DoesNotExist:
        spp_obj = crams_models.StorageProductProvisionId.objects.create(
            provision_id=provision_id,
            storage_product=sr_instance.storage_product)
    return spp_obj


def log_provision_id_change(product_request_instance, old_provision_id, user_obj, message=None):
    request = product_request_instance.request
    common_json = dict()
    common_json['id'] = product_request_instance.id
    common_json['storage_product'] = {
        'id': product_request_instance.storage_product.id,
        'name': product_request_instance.storage_product.name
    }
    common_json['request'] = {
        'id': request.id,
        'e_research_system': {
            'name': request.e_research_system.name,
            'e_research_body': request.e_research_system.e_research_body.name
        },
        'project': product_request_instance.request.project.title
    }
    before_json = copy.copy(common_json)
    if old_provision_id:
        before_json['provision_id'] = {
            'id': old_provision_id.id,
            'provision_id': old_provision_id.provision_id
        }

    after_json = copy.copy(common_json)
    provision_id = product_request_instance.provision_id
    if provision_id:
        after_json['provision_id'] = {
            'id': provision_id.id,
            'provision_id': provision_id.provision_id
        }

    if not message:
        sp = product_request_instance.storage_product.name
        old_pid = None
        if old_provision_id:
            old_pid = old_provision_id.provision_id
        new_pid = None
        if provision_id:
            new_pid = provision_id.provision_id
        message = 'Provision Id for {} changed from {} to {}'.format(sp, old_pid, new_pid)

    log_obj = log_process.log_change_provision_id(
        before_json=before_json, after_json=after_json, user_obj=user_obj, crams_request=request, message=message)

    return log_obj
