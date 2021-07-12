import datetime
from rest_framework import exceptions

from crams.models import CramsCommon, ArchivableModel
from crams.models import ProjectMemberStatus
from crams_log.models import AbstractLinkToCramsLog, CramsLog
from crams_contact.models import ContactRole
from crams.models import AbstractNotificationTemplate
from crams.models import EResearchBody, EResearchBodySystem, Question, Provider
from crams.models import FundingBody, FundingScheme
from django.core.validators import MaxValueValidator
from django.db import models

from crams_collection.models import Project, ProjectLog
from crams_log.models import CramsLog


class RequestStatus(models.Model):
    """
    RequestStatus Model
    """
    code = models.CharField(
        max_length=50
    )

    status = models.CharField(
        max_length=100
    )

    transient = models.BooleanField(default=False)

    class Meta:
        app_label = 'crams_allocation'

    def __str__(self):
        return '{} {} {}'.format(self.id, self.code, self.status)


class ERBRequestStatus(models.Model):
    request_status = models.ForeignKey(RequestStatus, related_name='erb_status_names', on_delete=models.DO_NOTHING)

    extension_count_data_point = models.SmallIntegerField(default=1)

    e_research_system = models.ForeignKey(EResearchBodySystem, blank=True, null=True, on_delete=models.DO_NOTHING)

    e_research_body = models.ForeignKey(EResearchBody, blank=True, null=True, on_delete=models.DO_NOTHING)

    display_name = models.CharField(max_length=99)

    class Meta:
        app_label = 'crams_allocation'

    def __str__(self):
        base_str = '{} <== {}'.format(self.display_name, self.request_status.status)
        if self.e_research_system:
            base_str += '/ {}'.format(self.e_research_system)
        elif self.e_research_body:
            base_str += '/ {}'.format(self.e_research_body)
        return base_str


class AllocationHome(models.Model):
    """
    Allocation Home
    """
    code = models.CharField(
        max_length=50, unique=True
    )
    description = models.CharField(
        max_length=200
    )

    class Meta:
        app_label = 'crams_allocation'

    def __str__(self):
        return '{} {} {}'.format(self.id, self.code, self.description)


class Request(CramsCommon):
    """
    Request Model
    """
    # For versioning
    current_request = models.ForeignKey(
        'Request', null=True, blank=True, related_name='history', on_delete=models.DO_NOTHING)

    project = models.ForeignKey(Project, related_name='requests', on_delete=models.DO_NOTHING)

    request_status = models.ForeignKey(RequestStatus, related_name='requests', on_delete=models.DO_NOTHING)

    data_sensitive = models.BooleanField(blank=True, null=True)

    funding_scheme = models.ForeignKey(
        FundingScheme, related_name='requests', blank=True, null=True, on_delete=models.DO_NOTHING)

    e_research_system = models.ForeignKey(
        EResearchBodySystem, related_name='eresearch_systems',
        blank=True, null=True, on_delete=models.DO_NOTHING)

    national_percent = models.PositiveSmallIntegerField(
        default=100, validators=[MaxValueValidator(100)]
    )

    transaction_id = models.CharField(max_length=99, blank=True, null=True)

    allocation_home = models.ForeignKey(
        AllocationHome, null=True, blank=True, related_name='requests', on_delete=models.DO_NOTHING)

    start_date = models.DateField(
        default=datetime.date.today
    )
    end_date = models.DateField()

    approval_notes = models.TextField(
        null=True,
        blank=True,
        max_length=1024
    )

    sent_email = models.BooleanField(default=True)

    allocation_extension_count = models.PositiveSmallIntegerField(default=0)

    sent_ext_support_email = models.BooleanField(default=False)

    class Meta:
        app_label = 'crams_allocation'

    def __str__(self):
        return '{}.{}'.format(self.id, self.project.title)


class RequestQuestionResponse(ArchivableModel):
    """
    RequestQuestionResponse Model
    """
    question_response = models.TextField(
        max_length=1024,
        blank=True
    )

    question = models.ForeignKey(
        Question, related_name='request_question_responses', on_delete=models.DO_NOTHING)

    request = models.ForeignKey(
        Request, related_name='request_question_responses', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_allocation'


class AllocationLog(AbstractLinkToCramsLog):
    crams_request_db_id = models.IntegerField()

    crams_project_db_id = models.IntegerField(blank=True, null=True)

    class Meta:
        app_label = 'crams_allocation'
        unique_together = ('crams_request_db_id', 'log_parent')

    def __str__(self):
        return '{} {}'.format(self.log_parent, self.crams_request_db_id)

    @classmethod
    def link_log(cls, log_obj, request_obj):
        if not isinstance(request_obj, Request):
            raise exceptions.ValidationError('Request object required to link log to AllocationLog')
        obj: AllocationLog
        obj, _ = cls.objects.get_or_create(
            log_parent=log_obj, crams_request_db_id=request_obj.id, crams_project_db_id=request_obj.project.id)

        return obj

    @classmethod
    def fetch_log_qs_for_request_id(cls, request_db_id):
        return CramsLog.objects.filter(allocationlog__crams_request_db_id=request_db_id)


class NotificationTemplate(AbstractNotificationTemplate):
    request_status = models.ForeignKey(RequestStatus, blank=True, null=True, on_delete=models.DO_NOTHING)
    project_member_status = models.ForeignKey(
        ProjectMemberStatus, blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    # contact_license_status = models.ForeignKey(
    #     'SoftwareLicenseStatus', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_allocation'
        unique_together = ('e_research_system',
                           'request_status',
                           'system_key',
                           'template_file_path')
        index_together = [
            'request_status', 'e_research_system', 'template_file_path']

    def __str__(self):
        return '{} / {} / {}'.format(self.template_file_path,
                                     self.request_status,
                                     self.e_research_system)


class NotificationContactRole(models.Model):
    notification = models.ForeignKey(NotificationTemplate,
                                     related_name='notify_roles', on_delete=models.DO_NOTHING)
    contact_role = models.ForeignKey(ContactRole,
                                     related_name='notifications', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_allocation'
        index_together = ['notification', 'contact_role']
        # indexes = [
        #     models.Index(fields=['notification', 'contact_role']),
        # ]

    def __str__(self):
        return '{} / {}'.format(self.notification, self.contact_role)
