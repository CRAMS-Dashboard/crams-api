# coding=utf-8
"""

"""
from crams.models import ProvisionableItem, ArchivableModel, AbstractAllocation
from crams.models import Question, ProductCommon, Zone
from django.db import models


class StorageType(models.Model):
    """
    StorageType Model
    """
    storage_type = models.CharField(
        max_length=100
    )

    class Meta:
        app_label = 'crams_storage'

    def __str__(self):
        return '{}'.format(self.storage_type)


class StorageProduct(ProductCommon):
    """
    StorageProduct Model
    """
    zone = models.ForeignKey(Zone, related_name='storage_products', null=True, blank=True, on_delete=models.DO_NOTHING)

    storage_type = models.ForeignKey(
        StorageType, related_name='storage_products', on_delete=models.DO_NOTHING)

    parent_storage_product = models.ForeignKey('StorageProduct', default=None,
                                               null=True, blank=True, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_storage'
        unique_together = ('name', 'e_research_system', 'storage_type', 'zone')
        index_together = ['name', 'e_research_system']
        # indexes = [
        #     models.Index(fields=['name', 'e_research_system']),
        # ]

    def __str__(self):
        return '{} - {}'.format(self.name, self.provider)


class StorageProductProvisionId(models.Model):
    provision_id = models.CharField(max_length=255, blank=True, null=True)

    storage_product = models.ForeignKey(StorageProduct, db_index=True, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = ('provision_id', 'storage_product')
        index_together = ['provision_id', 'storage_product']
        app_label = 'crams_storage'

    def __str__(self):
        return '{} / {}'.format(self.provision_id, self.storage_product.name)
