from django.db import models

# Create your models here.
from crams.models import EResearchBodyIDKey, FundingBody, EResearchBodySystem, EResearchBody


class AbstractNotificationTemplate(models.Model):
    funding_body = models.ForeignKey(FundingBody, blank=True, null=True,
                                     default=None,
                                     related_name='notification_templates', on_delete=models.DO_NOTHING)
    # request_status = models.ForeignKey(RequestStatus, blank=True, null=True, on_delete=models.DO_NOTHING)
    # project_member_status = models.ForeignKey(
    #     'ProjectMemberStatus', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    # contact_license_status = models.ForeignKey(
    #     'SoftwareLicenseStatus', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    system_key = models.ForeignKey(EResearchBodyIDKey,
                                   blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    template_file_path = models.CharField(max_length=99)
    alert_funding_body = models.BooleanField(default=False)
    e_research_system = models.ForeignKey(
        EResearchBodySystem, blank=True, null=True, default=None,
        related_name='notification_templates', on_delete=models.DO_NOTHING)
    e_research_body = models.ForeignKey(
        EResearchBody, blank=True, null=True, default=None, on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True

    def __str__(self):
        return '{} / {}'.format(self.template_file_path,
                                     self.e_research_system)
