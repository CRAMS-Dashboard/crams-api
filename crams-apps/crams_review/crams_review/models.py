from django.db import models

from crams.models import CramsCommon
from crams.models import EResearchBody
from crams_allocation.models import Request
from crams_contact.models import Contact
from crams_contact.models import ContactRole


class ReviewConfig(models.Model):
    e_research_body = models.ForeignKey(EResearchBody, on_delete=models.DO_NOTHING)

    email_notification_template_file = models.CharField(max_length=255,
                                                        blank=False,
                                                        null=False)

    internal_email = models.EmailField(blank=True,
                                       null=True)
    # number of months after project provisioning to start a review
    review_period_month = models.IntegerField(default=12) 

    # number of months before the review period to notify users about review
    review_notify_month = models.IntegerField(default=2)

    enable = models.BooleanField(default=True)

    class Meta:
        app_label = 'crams_review'

    def __str__(self):
        return '{}'.format(self.e_research_body.name)


class ReviewContactRole(models.Model):
    review_config = models.ForeignKey(ReviewConfig,
                                      related_name="contact_roles", on_delete=models.DO_NOTHING)

    contact_role = models.ForeignKey(ContactRole, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_review'

    def __str__(self):
        return '{} - {}'.format(self.review_config.e_research_body,
                                self.contact_role.name)


class ReviewDate(CramsCommon):
    review_date = models.DateTimeField()

    request = models.ForeignKey(Request, on_delete=models.DO_NOTHING)

    STATUS_CHOICES = (('P', 'Pending'),
                      ('S', 'Sent'),
                      ('K', 'Skipped'),
                      ('F', 'Failed'))

    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default='P')

    notes = models.TextField(
        null=True,
        blank=True
    )

    review_json = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        app_label = 'crams_review'

    def __str__(self):
        return '{} - {}'.format(self.request.project.title,
                                self.review_date)
