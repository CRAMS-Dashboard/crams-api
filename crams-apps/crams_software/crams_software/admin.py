from django.contrib import admin
from crams_software import models


class SoftwareLicenseAdmin(admin.ModelAdmin):
    """
    class SoftwareLicenseAdmin
    """
    list_display = ('software', 'end_date_ts',
                    'is_academic', 'is_restricted')
    list_filter = ['cluster', 'type']


# Register your models here.
admin.site.register(models.SoftwareProduct)
admin.site.register(models.SoftwareProductMetaData)
admin.site.register(models.SoftwareProductCategory)
admin.site.register(models.SoftwareLicense, SoftwareLicenseAdmin)
admin.site.register(models.SoftwareLicenseType)
admin.site.register(models.ContactSoftwareLicense)
admin.site.register(models.SoftwareUserEvent)
