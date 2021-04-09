# coding=utf-8
"""

"""
import datetime
import pytz
from django.db import models

from crams.models import CramsCommon, ProvisionableItem, ProvisionDetails, ArchivableModel
from crams.models import EResearchBody, EResearchBodySystem, EResearchBodyIDKey, Question, Provider
from crams_allocation.product_allocation.models import StorageRequest, StorageProductProvisionId
from crams_allocation.constants.db import REQUEST_STATUS_PROVISIONED, REQUEST_STATUS_PARTIAL_PROVISIONED


class IngestSource(models.Model):
    source = models.ForeignKey(EResearchBodySystem, on_delete=models.DO_NOTHING)
    location = models.CharField(max_length=47)

    class Meta:
        app_label = 'crams_resource_usage'

    def __str__(self):  # __unicode__ on Python 2
        return self.__unicode__()

    def __unicode__(self):
        return '{} / {}'.format(self.location, self.source)


class StorageUsageIngest(models.Model):
    extract_date = models.DateField(db_index=True)
    provision_id = models.ForeignKey(
        StorageProductProvisionId, related_name='ingests', db_index=True, on_delete=models.DO_NOTHING)
    reported_allocated_gb = models.FloatField(default=0.0)
    ingested_gb_disk = models.FloatField(default=0.0)
    ingested_gb_tape = models.FloatField(default=0.0)
    creation_ts = models.DateTimeField(auto_now_add=True, editable=False)
    reported_by = models.ForeignKey(IngestSource, on_delete=models.DO_NOTHING)
    related_storage_request = models.ForeignKey(
        StorageRequest, blank=True, null=True, db_index=True, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_resource_usage'
        index_together = ['provision_id', 'extract_date']
        # indexes = [
        #     models.Index(fields=['provision_id', 'extract_date']),
        #     models.Index(fields=['provision_id'],
        #                  name='ingest_provision_id_idx'),
        # ]

    def __str__(self):  # __unicode__ on Python 2
        return self.__unicode__()

    def __unicode__(self):
        return '{} / {}'.format(self.provision_id, self.extract_date)

    # def save(self, *args, **kwargs):
    #     if self.id:
    #         raise Exception('Update not allowed')
    #     super(StorageUsageIngest, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        raise Exception('Delete not allowed')

    @property
    def project(self):
        if self.related_storage_request:
            project = self.related_storage_request.request.project
            if project.current_project:
                project = project.current_project
            return project
        return self.current_request().project

    @property
    def storage_product(self):
        return self.provision_id.storage_product

    @property
    def total_ingested_gb(self):
        return self.ingested_gb_disk + self.ingested_gb_tape

    def is_duplicate(self):
        if not self.provision_id:
            return False

        try:
            StorageUsageIngest.objects.get(provision_id=self.provision_id,
                                           extract_date=self.extract_date)
        except StorageUsageIngest.DoesNotExist:
            return False
        except StorageUsageIngest.MultipleObjectsReturned:
            pass

        return True

    def current_storage_request(self):
        if self.related_storage_request:
            request = self.related_storage_request.request
            if request.current_request:
                request = request.current_request
            sr_qs = request.storage_requests.filter(storage_product=self.storage_product)
        else:
            sr_qs = StorageRequest.objects.filter(
                provision_id=self.provision_id,
                request__current_request__isnull=True)
        count = sr_qs.count()
        if count > 1:
            msg = 'ProvisionId {} related to multiple projects, pk={}'
            raise Exception(msg.format(self.provision_id, self.id))
        elif count == 0:
            msg = 'ProvisionId {} not related to current request'
            raise Exception(msg.format(self.provision_id))

        return sr_qs.latest('id')

    def last_provisioned_storage_request(
            self, max_date=None, enforce_max_date=False):
        qs = self.get_provisioned_storage_requests_qs()
        if max_date:
            ts = datetime.datetime(max_date.year, max_date.month, max_date.day)
            ts = ts.replace(tzinfo=pytz.UTC)
            qs_max_date = qs.filter(request__creation_ts__lte=ts)
            if qs_max_date.exists() or enforce_max_date:
                qs = qs_max_date
            else:
                print('no max date sr', max_date, self)

        if qs.exists():
            return qs.order_by('-id').first()
        return None

    def get_provisioned_storage_requests_qs(self):
        provision_status = [REQUEST_STATUS_PROVISIONED, REQUEST_STATUS_PARTIAL_PROVISIONED]
        request_status_filter = models.Q(
            request__request_status__code__in=provision_status,
            storage_product=self.storage_product,
            provision_id=self.provision_id
        )
        qs = StorageRequest.objects.filter(request_status_filter)
        return qs

    def current_request(self):
        return self.current_storage_request().request

    def get_allocated_gb(self, date_ts_required=None):
        provisioned_sr = self.last_provisioned_storage_request(
            max_date=date_ts_required, enforce_max_date=True)
        if provisioned_sr:
            return provisioned_sr.approved_quota_total
        return 0


class StorageInfrastructure(CramsCommon):
    name = models.CharField(max_length=99)

    display_name = models.CharField(max_length=999, blank=True, null=True)

    e_research_body = models.ForeignKey(EResearchBody, on_delete=models.DO_NOTHING)

    description = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'crams_resource_usage'

    def __str__(self):  # __unicode__ on Python 2
        return self.__unicode__()

    def __unicode__(self):
        return '{} / {}'.format(self.name, self.e_research_body)
