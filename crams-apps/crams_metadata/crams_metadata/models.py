from django.db import models
from django.db.models import Sum, Max

from crams import models as crams_models
from crams_allocation.allocation import models as allocation_models
from crams_contact import models as contact_models


class MetadataLabelConfig(models.Model):
    erb_label = models.OneToOneField(crams_models.EResearchBodyIDKey)

    enforce_allocation_quota = models.BooleanField(default=False)

    class Meta:
        app_label = 'metadata'


class ERBLabelMetaSequence(crams_models.CramsCommon):
    label = models.ForeignKey(crams_models.EResearchBodyIDKey,
                              related_name='allocation_metadata')

    sequence_number = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('label', 'sequence_number')
        app_label = 'metadata'

    def __str__(self):
        return '{}  {}'.format(self.label.key, self.sequence_number)

    def save(self, *args, **kwargs):
        if self.id:
            raise Exception('Update not allowed on ERB Label Sequence')
        return super().save(*args, **kwargs)  # Call the "real" save() method.

    @classmethod
    def get_next_sequence_number(cls, erb_id_key_obj):
        if not erb_id_key_obj:
            return 1
        if not isinstance(erb_id_key_obj, crams_models.EResearchBodyIDKey):
            msg = 'EResearchBodyIDKey object required to get next sequence no.'
            raise Exception(msg)
        seq_dict = erb_id_key_obj.allocation_metadata.aggregate(
            max_seq=Max('sequence_number'))
        current_max = seq_dict.get('max_seq')
        if not current_max:
            current_max = 0
        return current_max + 1


class ContactLabelMetaSequence(crams_models.CramsCommon):
    label = models.ForeignKey(contact_models.ContactLabel,
                              related_name='allocation_metadata')

    sequence_number = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('label', 'sequence_number')
        app_label = 'metadata'

    def __str__(self):
        return '{}  {}'.format(self.label.label_name, self.sequence_number)

    def save(self, *args, **kwargs):
        if self.id:
            raise Exception('Update not allowed on Contact Label Sequence')
        return super().save(*args, **kwargs)  # Call the "real" save() method.

    @classmethod
    def get_next_sequence_number(cls, contact_label_obj):
        if not isinstance(contact_label_obj, contact_models.ContactLabel):
            msg = 'ContactLabel object required to get next sequence no.'
            raise Exception(msg)
        seq_dict = contact_label_obj.allocation_metadata.aggregate(
            max_seq=Max('sequence_number'))
        current_max = seq_dict.get('max_seq')
        if not current_max:
            current_max = 0
        return current_max + 1


class StorageAllocationMetadata(crams_models.CramsCommon):
    provision_id = models.ForeignKey(allocation_models.StorageProductProvisionId,
                                     related_name='allocation_metadata')

    related_storage_request = models.ForeignKey(
        allocation_models.StorageRequest, blank=True, null=True, editable=False)

    allocation_gb = models.FloatField()

    organisation = models.ForeignKey(
        crams_models.Organisation, blank=True, null=True)

    erb_label = models.ForeignKey(ERBLabelMetaSequence,
                                  related_name='storage',
                                  blank=True, null=True)

    contact_label = models.ForeignKey(ContactLabelMetaSequence,
                                      related_name='storage',
                                      blank=True, null=True)

    review_date = models.DateField(blank=True, null=True)

    # put variable properties like title, description etc in json
    properties_json = models.TextField(blank=True, null=True)

    current_metadata = models.ForeignKey('StorageAllocationMetadata',
                                         null=True, blank=True,
                                         related_name='history')
    class Meta:
        app_label = 'metadata'

    def __str__(self):
        label = self.erb_label or self.contact_label
        return '{} - {} GB'.format(label, self.allocation_gb)

    @classmethod
    def available_quota(cls, sp_provision_id_obj):
        if not isinstance(sp_provision_id_obj,
                          crams_models.StorageProductProvisionId):
            msg = 'Provision Id object required to calculate availabe quota'
            raise Exception(msg)

        sr_provisioned = sp_provision_id_obj.last_provisioned_storage_request(
            enforce_max_date=True)
        if not sr_provisioned:
            return 0

        total_provisioned = sr_provisioned.approved_quota_total
        allocated_dict = sp_provision_id_obj.allocation_metadata.filter(
            current_metadata__isnull=True).aggregate(
            allocated_total=Sum('allocation_gb'))
        metadata_allocated = allocated_dict.get('allocated_total')
        if not metadata_allocated:
            return total_provisioned
        return total_provisioned - metadata_allocated
