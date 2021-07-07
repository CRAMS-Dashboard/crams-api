# coding=utf-8
"""
Crams Models
"""
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator
from django.contrib.auth import models as auth_models
from django.db import models
from rest_framework.authtoken.models import Token
from crams.utils import date_utils
from merc_common import settings
from crams.user_manager import UserManager


class CramsToken(Token):
    """
    CramsToken Model
    """
    ks_roles = models.TextField(null=True, blank=True)

    class Meta:
        app_label = 'crams'

    def is_expired(self):
        current_ts = date_utils.get_current_time_for_app_tz()
        elapsed_seconds = date_utils.get_seconds_elapsed(current_ts, self.created)
        return elapsed_seconds >= settings.TOKEN_EXPIRY_TIME_SECONDS


class User(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    username = models.CharField(max_length=128, unique=True)
    email = models.EmailField(max_length=75)
    keystone_uuid = models.CharField(max_length=64, blank=True, null=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active. '
                    'Unselect this instead of deleting accounts.'))
    first_name = models.CharField(_('first name'),
                                  max_length=30, blank=True, null=True)
    last_name = models.CharField(_('last name'),
                                 max_length=30, blank=True, null=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):  # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    class Meta:
        app_label = 'crams'


class CramsCommon(models.Model):
    """
    CramsCommon Model
    """
    creation_ts = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )
    last_modified_ts = models.DateTimeField(
        auto_now=True,
        editable=False
    )
    created_by = models.ForeignKey(
        User, related_name="%(class)s_created_by", blank=True, null=True, on_delete=models.DO_NOTHING)
    updated_by = models.ForeignKey(
        User, related_name="%(class)s_updated_by", blank=True, null=True, on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True
        app_label = 'crams'


class ArchivableModel(models.Model):
    archive_ts = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
        app_label = 'crams'

    def archive_instance(self):
        self.archive_ts = date_utils.get_current_time_for_app_tz()
        self.save()

    @classmethod
    def get_current_for_qs(cls, archivable_qs):
        if isinstance(archivable_qs.model, type(ArchivableModel)):
            return archivable_qs.filter(archive_ts__isnull=True)


class UserEvents(CramsCommon):
    """
    UserEvents Model
    """
    event_message = models.TextField()

    related_user = models.ForeignKey(User, blank=True, null=True, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams'


class Provider(CramsCommon):
    """
    Provider Model
    Each provider object in crams represents an infrastructure provisioning team.
    The membership of this provisioning team is left undefined in this module.
    Instead it is expected that the provider object is associated with a set of eResearch Body systems
    """
    name = models.CharField(max_length=200, unique=False)
    start_date = models.DateField(auto_now_add=True, editable=False)
    active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    @property
    def provider_role(self):
        return self.name.strip().lower() + '_provider'

    def get_status_str(self):
        """

        get status as string
        :return:
        """
        if not self.active:
            return 'inActive'
        return 'current'

    class Meta:
        app_label = 'crams'

    def __str__(self):
        return '{}'.format(self.name)


class ProvisionDetails(CramsCommon):
    """
    ProvisionDetails Model
    The status flow is
    - From Nothing to Sent
    - From Sent to Provisioned or Failed
    - From Provisioned to Updated
    - From Failed to Updated
    - From Updated to Update Sent
    - From Update Sent to Provisioned or Failed
    """
    UNKNOWN = '?'
    SENT = 'S'
    PROVISIONED = 'P'
    POST_PROVISION_UPDATE = 'U'
    POST_PROVISION_UPDATE_SENT = 'X'
    FAILED = 'F'
    RESEND_LATER = 'L'
    SET_OF_SENT = frozenset([SENT, POST_PROVISION_UPDATE_SENT])
    READY_TO_SEND_SET = frozenset([RESEND_LATER, POST_PROVISION_UPDATE])
    STATUS_CHOICES = ((SENT, 'Sent'), (PROVISIONED, 'Provisioned'),
                      (FAILED, 'Failed'), (RESEND_LATER, 'Resend'),
                      (POST_PROVISION_UPDATE, 'Updated'),
                      (POST_PROVISION_UPDATE_SENT, 'Update Sent'),
                      (UNKNOWN, '???'))
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=SENT)
    message = models.TextField(blank=True, null=True)
    parent_provision_details = models.ForeignKey(
        'ProvisionDetails', blank=True, null=True, related_name='history', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams'

    def __str__(self):
        return '{}. {} : {}'.format(self.id, self.status, self.message)


class ProvisionableItem(models.Model):
    """
    ProvisionableItem Model
    """
    provision_details = models.OneToOneField(
        ProvisionDetails, blank=True, null=True, related_name='%(class)s', on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True
        app_label = 'crams'

    def get_provider(self):
        """
        get provider
        :raise NotImplementedError:
        """
        raise NotImplementedError(
            'Get Provider not implemented for abstract Product Request model')


class EResearchBody(models.Model):
    name = models.CharField(max_length=200, db_index=True)

    email = models.EmailField(null=True, blank=True)

    class Meta:
        app_label = 'crams'
        # indexes = [
        #     models.Index(fields=['name'], name='erb_name_idx'),
        # ]

    def __str__(self):
        return self.name

    @property
    def admin_role(self):
        return self.name.strip().lower() + '_erb_admin'

    @property
    def tenancy_manager_role(self):
        return self.name.strip().lower() + '_erb_tenancy_manager'


class EResearchBodySystem(models.Model):
    e_research_body = models.ForeignKey(EResearchBody, related_name='systems', on_delete=models.DO_NOTHING)

    name = models.CharField(max_length=200, db_index=True)

    email = models.EmailField(null=True, blank=True)

    class Meta:
        app_label = 'crams'
        unique_together = ('name', 'e_research_body')
        index_together = ['name', 'e_research_body']
        # indexes = [
        #     models.Index(fields=['name', 'e_research_body']),
        #     models.Index(fields=['name'], name='erb_system_name_idx'),
        # ]

    def __str__(self):
        return self.name

    @property
    def admin_role(self):
        return self.name.strip().lower() + '_erbs_admin'

    @property
    def approver_role(self):
        return self.name.strip().lower() + '_erbs_approver'


class EResearchBodyDelegate(models.Model):
    e_research_body = models.ForeignKey(
        EResearchBody, related_name='delegates', on_delete=models.DO_NOTHING)

    name = models.CharField(max_length=200, db_index=True)

    email = models.EmailField(null=True, blank=True)

    class Meta:
        app_label = 'crams'
        unique_together = ('name', 'e_research_body')
        index_together = ['name', 'e_research_body']
        # indexes = [
        #     models.Index(fields=['name', 'e_research_body']),
        #     models.Index(fields=['name'], name='erb_delegate_name_idx'),
        # ]

    def __str__(self):
        return self.name

    @property
    def approver_role(self):
        return self.name.strip().lower() + '_delegate_approver'


class EResearchBodyIDKey(models.Model):
    """
    EResearchBodyIDKey Model
    """
    ID_KEY = 'I'
    LABEL = 'L'
    METADATA = 'M'
    TYPE_CHOICES = ((ID_KEY, 'Id_Key'), (LABEL, 'Label'),
                    (METADATA, 'Metadata'))
    type = models.CharField(
        max_length=1, choices=TYPE_CHOICES, default=ID_KEY)

    key = models.CharField(max_length=100)

    e_research_body = models.ForeignKey(EResearchBody, blank=True, null=True, on_delete=models.DO_NOTHING)

    description = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'crams'
        unique_together = ('key', 'e_research_body')

    def __str__(self):
        return '{} / {}'.format(self.key, self.e_research_body)


class Question(models.Model):
    """
    Question Model
    """
    key = models.CharField(
        max_length=50, unique=True
    )

    question_type = models.CharField(
        max_length=200
    )

    question = models.CharField(
        max_length=200
    )

    class Meta:
        app_label = 'crams'

    def __str__(self):
        return '{} {} {}'.format(self.key, self.question_type, self.question)


class FundingBody(models.Model):
    """
    FundingBody Model
    """
    name = models.CharField(
        max_length=200
    )

    email = models.EmailField(null=True, blank=True)

    class Meta:
        app_label = 'crams'

    def __str__(self):
        return '{} - {}'.format(self.name, self.email)


class FundingScheme(models.Model):
    """
    FundingScheme Model
    """
    funding_scheme = models.CharField(
        max_length=200
    )

    funding_body = models.ForeignKey(
        FundingBody, related_name='funding_schemes', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams'

    def __str__(self):
        return '{} {}'.format(self.funding_body.name, self.funding_scheme)


class Duration(models.Model):
    """
    Duration Model
    """
    duration = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    duration_label = models.CharField(
        max_length=50
    )

    class Meta:
        app_label = 'crams'

    def __str__(self):
        return '{} {}'.format(self.duration, self.duration_label)


class FORCode(models.Model):
    """
    FORCode Model
    """
    code = models.CharField(
        max_length=50
    )

    description = models.CharField(
        max_length=200
    )

    class Meta:
        app_label = 'crams'

    def __str__(self):
        return '{} {}'.format(self.code, self.description)


class SEOCode(models.Model):
    code = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    class Meta:
        app_label = 'crams'

    def __str__(self):  # __unicode__ on Python 2
        return self.__unicode__()

    def __unicode__(self):
        return str(self.code)


class CramsSequence(models.Model):
    code = models.CharField(max_length=255, primary_key=True)
    last_sequence_num = models.IntegerField(default=0)

    class Meta:
        app_label = 'crams'

    def __str__(self):  # __unicode__ on Python 2
        return self.__unicode__()

    def __unicode__(self):
        return str(self.code + ' : ' + str(self.last_sequence_num))

    @classmethod
    def get_code_increment_sequence(cls, code):
        seq, created = CramsSequence.objects.get_or_create(code=code)
        seq.last_sequence_num += 1
        seq.save()
        return seq


class SupportEmailContact(models.Model):
    description = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(db_index=True)
    e_research_body = models.ForeignKey(EResearchBody, on_delete=models.DO_NOTHING)
    e_research_system = models.ForeignKey(
        EResearchBodySystem, null=True, blank=True, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams'

    def __str__(self):
        return '{} {}'.format(self.description, self.email)


class MessageOfTheDay(CramsCommon):
    message = models.CharField(max_length=1500, blank=True, null=True)
    e_research_body = models.ForeignKey(EResearchBody, null=True, blank=True, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams'

    def __str__(self):
        return '{}'.format(self.message)


class CostUnitType(models.Model):
    unit_name = models.CharField(max_length=19)

    class Meta:
        app_label = 'crams'

    def __str__(self):
        return self.unit_name


class ProductCommon(models.Model):
    """
    ProductCommon Model
    """
    name = models.CharField(max_length=200)

    funding_body = models.ForeignKey(FundingBody, related_name='%(class)s', on_delete=models.DO_NOTHING)

    e_research_system = models.ForeignKey(
        EResearchBodySystem, related_name='%(class)s',
        blank=True, null=True, default=None, on_delete=models.DO_NOTHING)

    provider = models.ForeignKey(Provider, related_name='%(class)s', on_delete=models.DO_NOTHING)

    unit_cost = models.FloatField(default=0.0)

    operational_cost = models.FloatField(default=0.0)

    cost_unit_type = models.ForeignKey(CostUnitType, related_name='%(class)s',
                                       blank=True, null=True, on_delete=models.DO_NOTHING)

    capacity = models.FloatField(default=0.0)

    class Meta:
        abstract = True
        unique_together = ('name', 'e_research_system')
        index_together = ['name', 'e_research_system']
        app_label = 'crams'

    def __str__(self):
        return '{} {}'.format(self.id, self.name)


class Zone(models.Model):
    """
    Zone Model
    """
    name = models.CharField(max_length=64)
    description = models.TextField()

    class Meta:
        app_label = 'crams'

    def __str__(self):
        return '{}'.format(self.name)


class AbstractAllocation(ProvisionableItem):
    """
    AbstractAllocation Model
    """
    current_quota = models.FloatField(default=0.0)

    requested_quota_change = models.FloatField(default=0.0)

    approved_quota_change = models.FloatField(default=0.0)

    class Meta:
        app_label = 'crams_storage'
        abstract = True

    @property
    def requested_quota_total(self):
        return self.current_quota + self.requested_quota_change

    @property
    def approved_quota_total(self):
        return self.current_quota + self.approved_quota_change


class ProjectMemberStatus(models.Model):
    """
    ProjectMemberStatus Model
    """
    code = models.CharField(
        max_length=50
    )

    status = models.CharField(
        max_length=100
    )

    class Meta:
        app_label = 'crams'

    def __str__(self):
        return '{} {} {}'.format(self.id, self.code, self.status)


class AbstractNotificationTemplate(models.Model):
    funding_body = models.ForeignKey(FundingBody, blank=True, null=True, default=None,
                                     related_name='notification_templates', on_delete=models.DO_NOTHING)
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
        return '{} {}'.format(self.template_file_path, self.e_research_system)
