from django.db import models

from crams.models import CramsCommon, ProvisionableItem, ProvisionDetails, ArchivableModel
from crams.models import EResearchBody, EResearchBodySystem, EResearchBodyIDKey, Question, Provider
from crams_allocation.product_allocation.models import StorageRequest, StorageProductProvisionId


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

    def current_storage_request(self, ignore_exception=False):
        try:
            return self.provision_id.current_storage_request()
        except Exception as e:
            if not ignore_exception:
                raise e

    # def save(self, *args, **kwargs):
    #     if self.id:
    #         raise Exception('Update not allowed')
    #     super(StorageUsageIngest, self).save(*args, **kwargs)

    def delete(self, using=None):
        raise Exception('Delete not allowed')

    @property
    def project(self):
        if self.related_storage_request:
            project = self.related_storage_request.request.project
            if project.current_project:
                project = project.current_project
            return project
        return self.provision_id.current_request.project

    @property
    def storage_product(self):
        return self.provision_id.storage_product

    @property
    def total_ingested_gb(self):
        return self.ingested_gb_disk + self.ingested_gb_tape

    @property
    def allocated_gb(self):
        return self.provision_id.get_allocated_gb()

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


# class IngestSource(models.Model):
#     source = models.ForeignKey(EResearchBodySystem, on_delete=models.DO_NOTHING)
#     location = models.CharField(max_length=47)
#
#     class Meta:
#         app_label = 'crams_resource_usage'
#
#     def __str__(self):  # __unicode__ on Python 2
#         return self.__unicode__()
#
#     def __unicode__(self):
#         return '{} / {}'.format(self.location, self.source)
#
#
# class StorageUsageIngest(models.Model):
#     extract_date = models.DateField(db_index=True)
#     provision_id = models.ForeignKey(
#         StorageProductProvisionId, related_name='ingests', db_index=True, on_delete=models.DO_NOTHING)
#     reported_allocated_gb = models.FloatField(default=0.0)
#     ingested_gb_disk = models.FloatField(default=0.0)
#     ingested_gb_tape = models.FloatField(default=0.0)
#     creation_ts = models.DateTimeField(auto_now_add=True, editable=False)
#     reported_by = models.ForeignKey(IngestSource, on_delete=models.DO_NOTHING)
#     related_storage_request = models.ForeignKey(
#         StorageRequest, blank=True, null=True, db_index=True, on_delete=models.DO_NOTHING)
#
#     class Meta:
#         app_label = 'crams'
#         index_together = ['provision_id', 'extract_date']
#         # indexes = [
#         #     models.Index(fields=['provision_id', 'extract_date']),
#         #     models.Index(fields=['provision_id'],
#         #                  name='ingest_provision_id_idx'),
#         # ]
#
#     def __str__(self):  # __unicode__ on Python 2
#         return self.__unicode__()
#
#     def __unicode__(self):
#         return '{} / {}'.format(self.provision_id, self.extract_date)
#
#     def current_storage_request(self, ignore_exception=False):
#         s_request = self.provision_id.storage_requests.filter(
#             request__current_request__isnull=True)
#         count = s_request.count()
#         if count > 1:
#             msg = 'ProvisionId {} related to multiple projects, pk={}'
#             raise Exception(msg.format(self.provision_id, self.id))
#         elif count == 0:
#             s_request = self.provision_id.storage_requests.all()
#             if not s_request.exists():
#                 if not ignore_exception:
#                     msg = 'ProvisionId {} not related to request'
#                     raise Exception(msg.format(self.provision_id))
#                 return None
#         return s_request.latest('id')
#
#     @property
#     def project(self):
#         def get_current_project(project_obj):
#             if project_obj.current_project:
#                 project_obj = project_obj.current_project
#             return project_obj
#         if self.related_storage_request:
#             project = self.related_storage_request.request.project
#             return get_current_project(project)
#         return get_current_project(self.current_storage_request().request.project)
#
#     @property
#     def storage_product(self):
#         return self.provision_id.storage_product
#
#     @property
#     def total_ingested_gb(self):
#         return self.ingested_gb_disk + self.ingested_gb_tape
#
#     @property
#     def get_allocated_gb(self, date_ts_required=None):
#         qs = self.provision_id.storage_requests.filter(
#             request__request_status__code=REQUEST_STATUS_PROVISIONED)
#         if date_ts_required:
#             qs = qs.filter(request__creation_ts__lte=date_ts_required)
#         if qs.count() == 0:
#             return 0
#         sr = qs.latest('id')
#         return sr.approved_quota_total
#
#     def is_duplicate(self):
#         if not self.provision_id:
#             return False
#
#         try:
#             StorageUsageIngest.objects.get(provision_id=self.provision_id,
#                                            extract_date=self.extract_date)
#         except StorageUsageIngest.DoesNotExist:
#             return False
#         except StorageUsageIngest.MultipleObjectsReturned:
#             pass
#
#         return True
#
#
# class StorageInfrastructure(CramsCommon):
#     name = models.CharField(max_length=99)
#
#     display_name = models.CharField(max_length=999, blank=True, null=True)
#
#     e_research_body = models.ForeignKey(EResearchBody, on_delete=models.DO_NOTHING)
#
#     description = models.TextField(blank=True, null=True)
#
#     class Meta:
#         app_label = 'crams'
#
#     def __str__(self):  # __unicode__ on Python 2
#         return self.__unicode__()
#
#     def __unicode__(self):
#         return '{} / {}'.format(self.name, self.e_research_body)
