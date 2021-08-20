# coding=utf-8
"""

"""
from crams_allocation.models import Request
from crams_allocation.constants.db import REQUEST_STATUS_PROVISIONED
from crams.models import AbstractAllocation, EResearchBodySystem, EResearchBody
from crams_storage.models import StorageProduct, StorageProductProvisionId
from crams_compute.models import AbstractComputeAllocation
from crams.models import ArchivableModel
from crams.models import Question, CramsCommon
from django.db import models


class StorageRequest(AbstractAllocation):
    request = models.ForeignKey(Request, related_name='storage_requests', on_delete=models.DO_NOTHING)

    storage_product = models.ForeignKey(
        StorageProduct, related_name='storage_requests', on_delete=models.DO_NOTHING)

    provision_id = models.ForeignKey(StorageProductProvisionId,
                                     blank=True, null=True, db_index=True,
                                     related_name='storage_requests', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_allocation'

    def get_provider(self):
        """
        :return: product provider
        """
        return self.storage_product.provider

    def __str__(self):
        return '{}/{}: {} {}'.format(self.id, self.request.id, self.storage_product.name, self.requested_quota_total)


class StorageRequestQuestionResponse(ArchivableModel):
    """
    StorageRequestQuestionResponse Model
    """
    question_response = models.TextField(
        max_length=1024,
        blank=True
    )

    question = models.ForeignKey(
        Question, related_name='storage_question_responses', on_delete=models.DO_NOTHING)

    storage_allocation = models.ForeignKey(
        StorageRequest, related_name='storage_question_responses', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_allocation'


class ComputeRequest(AbstractComputeAllocation):
    request = models.ForeignKey(Request, related_name='compute_requests', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_allocation'

    def __str__(self):
        return '{}/CR:{}: {} {} {}'.format(self.id, self.request.id, self.instances, self.cores, self.core_hours)

    @classmethod
    def current_request_for_compute_provision_id(cls, compute_request_provision_id_obj):
        compute_request = compute_request_provision_id_obj.compute_allocation
        if not isinstance(compute_request, cls):
            msg = 'ComputeAllocation object is not an instance of {}'.format(cls.Meta.__name__)
            raise Exception(msg)

        if compute_request.request.current_request:
            return compute_request.request.current_request
        return compute_request.request


class ComputeRequestQuestionResponse(ArchivableModel):
    """
    ComputeAllocationQuestionResponse Model
    """
    question_response = models.TextField(
        max_length=1024,
        blank=True
    )

    question = models.ForeignKey(
        Question, related_name='compute_question_responses', on_delete=models.DO_NOTHING)

    compute_request = models.ForeignKey(
        ComputeRequest, related_name='compute_question_responses', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_allocation'
