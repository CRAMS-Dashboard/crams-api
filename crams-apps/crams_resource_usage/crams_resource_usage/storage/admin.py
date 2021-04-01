from django.contrib import admin

# Register your models here.
from crams_resource_usage.storage.models import StorageUsageIngest, IngestSource


class StorageUsageIngestAdmin(admin.ModelAdmin):
    """
    class StorageUsageIngestAdmin
    """
    list_display = (
        'extract_date', 'project', 'storage_product',
        'ingested_gb_disk', 'ingested_gb_tape'
    )
    list_filter = ['provision_id__storage_product']


admin.site.register(StorageUsageIngest, StorageUsageIngestAdmin)
admin.site.register(IngestSource)
