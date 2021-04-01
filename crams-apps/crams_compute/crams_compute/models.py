# Create your models here.

from crams.models import ProvisionableItem
from crams.models import ProductCommon
from django.db import models
from django.core.validators import MinValueValidator


class ComputeProduct(ProductCommon):
    """
    ComputeProduct Model
    """

    class Meta:
        unique_together = ('name', 'e_research_system')
        index_together = ['name', 'e_research_system']
        app_label = 'crams_compute'


class ComputeProductProvisionId(models.Model):
    provision_id = models.CharField(max_length=255, blank=True, null=True)

    compute_product = models.ForeignKey(ComputeProduct, db_index=True, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = ('provision_id', 'compute_product')
        index_together = ['provision_id', 'compute_product']
        app_label = 'crams_compute'

    def __str__(self):
        return '{} / {}'.format(self.provision_id, self.compute_product.name)


class AbstractComputeAllocation(ProvisionableItem):
    """
    This model must be replaced with newer compute allocation
     - by breaking down instance, core and core_hours as separate product
    """
    instances = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    approved_instances = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    cores = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    approved_cores = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    core_hours = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    approved_core_hours = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    compute_product = models.ForeignKey(
        ComputeProduct, related_name='compute_requests', on_delete=models.DO_NOTHING)

    def get_provider(self):
        """
        get_provider

        :return:
        """
        return None

    class Meta:
        abstract = True

    def __str__(self):
        return '{}: {} {} {}'.format(self.pk, self.instances, self.cores, self.core_hours)
