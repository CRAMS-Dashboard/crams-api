from django.db import models

from crams import models as crams
from crams_contact.models import Contact


class SoftwareProductCategory(models.Model):
    category = models.CharField(max_length=99)

    active = models.BooleanField(default=True)

    class Meta(object):
        app_label = 'crams_software'

    def __str__(self):
        return self.category


class SoftwareProduct(crams.ProvisionableItem):
    name = models.CharField(max_length=99)

    version = models.CharField(max_length=22, blank=True, null=True)

    e_research_body = models.ForeignKey(crams.EResearchBody, on_delete=models.DO_NOTHING)

    category = models.ForeignKey(SoftwareProductCategory, on_delete=models.DO_NOTHING)

    description = models.TextField(default='')

    active = models.BooleanField(default=True)

    class Meta(object):
        app_label = 'crams_software'
        unique_together = ('name', 'e_research_body')
        index_together = ['name', 'e_research_body']

    def __str__(self):
        return '{} version {}'.format(self.name, self.version)


class SoftwareProductMetaData(models.Model):
    name = models.ForeignKey(crams.EResearchBodyIDKey, on_delete=models.DO_NOTHING)

    value = models.CharField(max_length=99)  # mysql innoDB size limit 767

    software = models.ForeignKey(SoftwareProduct, related_name='metadata', on_delete=models.DO_NOTHING)

    class Meta(object):
        app_label = 'crams_software'
        unique_together = ('name', 'software', 'value')


class SoftwareLicenseType(models.Model):
    type = models.CharField(max_length=99)

    end_date_ts = models.DateTimeField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    class Meta(object):
        app_label = 'crams_software'
        unique_together = ('type', 'end_date_ts')

    def __str__(self):
        return self.type


class SoftwareLicense(models.Model):
    version = models.CharField(max_length=22, blank=True, null=True)

    cluster = models.ManyToManyField(crams.EResearchBodySystem)

    end_date_ts = models.DateTimeField(blank=True, null=True)

    software = models.ForeignKey(SoftwareProduct, related_name='licenses', on_delete=models.DO_NOTHING)

    is_academic = models.BooleanField(default=False)

    is_restricted = models.BooleanField(default=True)

    homepage = models.URLField(blank=True, null=True)

    type = models.ForeignKey(SoftwareLicenseType, on_delete=models.DO_NOTHING)

    start_date = models.DateField()

    license_text = models.TextField(blank=True, null=True)

    class Meta(object):
        app_label = 'crams_software'
        unique_together = ('software', 'type', 'end_date_ts')

    def __str__(self):
        return '{}.{}'.format(self.software, self.type)


class ContactSoftwareLicense(crams.ProvisionableItem):
    REQUEST_ACCESS = 'R'
    APPROVED = 'A'
    DECLINED = 'D'
    ACTION_CHOICES = (
        (REQUEST_ACCESS, 'Requested'),
        (APPROVED, 'Approved'),
        (DECLINED, 'Declined')
    )

    contact = models.ForeignKey(
        Contact, related_name='software_licenses', on_delete=models.DO_NOTHING)

    status = models.CharField(max_length=1, choices=ACTION_CHOICES)

    license = models.ForeignKey(SoftwareLicense, related_name='user_licenses', on_delete=models.DO_NOTHING)

    notes = models.TextField(null=True, blank=True)

    accepted_ts = models.DateTimeField(auto_created=True)

    end_date_ts = models.DateTimeField(blank=True, null=True)

    class Meta(object):
        app_label = 'crams_software'
        unique_together = ('contact', 'license', 'end_date_ts')

    def __str__(self):
        return '{}.{}'.format(self.contact, self.license)

    @classmethod
    def convert_display_to_status(cls, display_str):
        for k, v in cls.ACTION_CHOICES:
            if v.lower() == display_str.strip().lower():
                return k
        return None


class SoftwareUserEvent(crams.UserEvents):
    CREATE_SOFTWARE_LICENSE = 'CSL'
    UPDATE_SOFTWARE_LICENSE = 'USL'
    ACTION_CHOICES = (
        (CREATE_SOFTWARE_LICENSE, 'Create New Software License'),
        (UPDATE_SOFTWARE_LICENSE, 'Update Software License')
    )
    action = models.CharField(max_length=3, choices=ACTION_CHOICES)

    pre_event_json = models.TextField(blank=True)

    post_event_json = models.TextField(blank=True)

    class Meta(object):
        app_label = 'crams_software'

    def __str__(self):
        return '{}.{}'.format(self.get_action_display(), self.related_user)
