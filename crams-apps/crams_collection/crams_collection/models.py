from django.db import models
from rest_framework import exceptions

# Create your models here.
from django.core.validators import MinValueValidator, MaxValueValidator

from crams.models import CramsCommon, ProvisionableItem, ProvisionDetails, ArchivableModel, FORCode
from crams.models import EResearchBodyIDKey, Question
from crams_contact.models import Organisation, Faculty, Department
from crams_contact.models import Contact, ContactRole
from crams_log.models import AbstractLinkToCramsLog, CramsLog


class Project(CramsCommon):
    """
    Project Model
    """
    # for project versioning, if current_project is null which means it's a
    # latest project request
    current_project = models.ForeignKey('Project', null=True, blank=True, on_delete=models.DO_NOTHING)

    department = models.ForeignKey(
        Department, null=True, blank=True, related_name='projects', on_delete=models.DO_NOTHING)

    title = models.CharField(
        max_length=255
    )

    description = models.CharField(
        max_length=9999
    )

    notes = models.TextField(
        null=True,
        blank=True,
        max_length=1024
    )

    crams_id = models.CharField(
        null=True,
        blank=True,
        max_length=255
    )

    class Meta:
        app_label = 'crams_collection'

    def __str__(self):
        if self.current_project:
            return '{}.{} - (Parent) {}'.format(self.id,
                                                self.title,
                                                self.current_project.id,
                                                self.crams_id)
        else:
            return '{}.{}'.format(self.title, self.pk)

    @property
    def project_ids(self):
        return ProjectID.objects.filter(
            project=self, parent_erb_project_id__isnull=True)


class ProjectContact(models.Model):
    """
    ProjectContact Model
    """
    project = models.ForeignKey(Project, related_name='project_contacts', on_delete=models.DO_NOTHING)
    contact = models.ForeignKey(Contact, related_name='project_contacts', on_delete=models.DO_NOTHING)
    contact_role = models.ForeignKey(ContactRole, related_name='project_contacts', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_collection'
        unique_together = ('project', 'contact', 'contact_role')
        index_together = ['project', 'contact', 'contact_role']
        # indexes = [
        #     models.Index(fields=['project', 'contact', 'contact_role']),
        # ]


class ProjectProvisionDetails(models.Model):
    """
    ProjectProvisionDetails Model
    """
    project = models.ForeignKey(
        Project, related_name='linked_provisiondetails', on_delete=models.DO_NOTHING)
    provision_details = models.ForeignKey(
        ProvisionDetails, related_name='linked_projects', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_collection'


class ProjectQuestionResponse(ArchivableModel):
    """
    ProjectQuestionResponse Model
    """
    question_response = models.TextField(
        max_length=1024,
        blank=True

    )

    question = models.ForeignKey(
        Question, related_name='project_question_responses', on_delete=models.DO_NOTHING)

    project = models.ForeignKey(
        Project, related_name='project_question_responses', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_collection'


class ProjectID(ProvisionableItem):
    """
    ProjectID Model
    """
    identifier = models.CharField(max_length=64)

    project = models.ForeignKey(Project, related_name='archive_project_ids', on_delete=models.DO_NOTHING)

    system = models.ForeignKey(EResearchBodyIDKey, related_name='project_ids', on_delete=models.DO_NOTHING)

    parent_erb_project_id = models.ForeignKey(
        'ProjectID', blank=True, null=True, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_collection'
        index_together = ['identifier', 'project', 'system']
        # indexes = [
        #     models.Index(fields=['identifier', 'project', 'system']),
        #  ]

    @property
    def current_project(self):
        return self.project.current_project or self.project

    @property
    def is_history(self):
        return self.project.current_project is not None

    def __str__(self):
        return '{} - {} {}'.format(self.system, self.identifier, self.project)


class OrganisationContact(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.DO_NOTHING)
    organisation = models.ForeignKey(Organisation, null=True, blank=True, on_delete=models.DO_NOTHING)
    faculty = models.ForeignKey(Faculty, null=True, blank=True, on_delete=models.DO_NOTHING)
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_collection'

    def __str__(self):  # __unicode__ on Python 2
        return self.__unicode__()

    def __unicode__(self):
        return str(self.contact.email)


class Domain(models.Model):
    """
    Domain Model
    """
    percentage = models.FloatField(
        default=0.0
    )

    project = models.ForeignKey(Project, related_name='domains', on_delete=models.DO_NOTHING)

    for_code = models.ForeignKey(FORCode, related_name='domains', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_collection'

    def __str__(self):
        return '{} {} {}'.format(
            self.project.title,
            self.for_code.code,
            self.percentage)


class Publication(ArchivableModel):
    """
    Publication Model
    """
    reference = models.CharField(
        max_length=255
    )

    project = models.ForeignKey(Project, related_name='publications', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_collection'

    def __str__(self):
        return '{}'.format(self.reference)


class GrantType(models.Model):
    """
    GrantType Model
    """
    description = models.CharField(
        max_length=200
    )

    class Meta:
        app_label = 'crams_collection'

    def __str__(self):
        return '{} {}'.format(self.pk, self.description)


class Grant(ArchivableModel):
    """
    Grant Model
    """
    project = models.ForeignKey(Project, related_name='grants', on_delete=models.DO_NOTHING)

    grant_type = models.ForeignKey(GrantType, related_name='grants', on_delete=models.DO_NOTHING)

    funding_body_and_scheme = models.CharField(
        blank=False, max_length=200
    )

    grant_id = models.CharField(
        blank=True, null=True, max_length=200
    )

    start_year = models.IntegerField(
        blank=False,
        validators=[MinValueValidator(1970), MaxValueValidator(3000)],
        error_messages={
            'min_value': 'Please input a year between 1970 ~ 3000',
            'max_value': 'Please input a year between 1970 ~ 3000'}
    )

    duration = models.IntegerField(
        blank=False,
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        error_messages={
            'min_value': 'Please enter funding duration (in months 1-1000).',
            'max_value': 'Please enter funding duration (in months 1~1000).'}
    )

    total_funding = models.FloatField(
        blank=True,
        default=0.0,
    )

    class Meta:
        app_label = 'crams_collection'

    def __str__(self):
        return '{} {} {}'.format(
            self.grant_type,
            self.funding_body_and_scheme,
            self.start_year)


class ProjectLog(AbstractLinkToCramsLog):
    crams_project_db_id = models.IntegerField()

    class Meta:
        app_label = 'crams_collection'
        unique_together = ('crams_project_db_id', 'log_parent')

    def __str__(self):
        return '{} {}'.format(self.log_parent, self.crams_project_db_id)

    @classmethod
    def link_log(cls, log_obj, project_obj):
        if not isinstance(project_obj, Project):
            raise exceptions.ValidationError('ProjectLog: Project object required to link crams_log')
        obj, _ = cls.objects.get_or_create(log_parent=log_obj, crams_project_db_id=project_obj.id)
        return obj

    @classmethod
    def fetch_log_qs(cls, project_db_id):
        return CramsLog.objects.filter(projectlog__crams_project_db_id=project_db_id)
