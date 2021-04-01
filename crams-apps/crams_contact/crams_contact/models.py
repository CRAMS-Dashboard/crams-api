from django.db import models
from rest_framework import exceptions

# Create your models here.

from crams import models as crams_models
from crams_contact.utils import validators
from crams_log.models import AbstractLinkToCramsLog


class Organisation(models.Model):
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=50, db_index=True)
    ands_url = models.URLField(null=True, blank=True)
    notification_email = models.EmailField()

    class Meta:
        app_label = 'crams_contact'

    def __str__(self):  # __unicode__ on Python 2
        return self.__unicode__()

    def __unicode__(self):
        return str(self.short_name)

    @property
    def manager_role(self):
        return 'pk_{}.organisation_manager'.format(self.id)


class Faculty(models.Model):
    faculty_code = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    organisation = models.ForeignKey(Organisation, related_name='faculties', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_contact'

    def __str__(self):  # __unicode__ on Python 2
        return self.__unicode__()

    def __unicode__(self):
        return '{} / {}'.format(self.name, self.organisation)

    @property
    def manager_role(self):
        return 'pk_{}.faculty_manager'.format(self.id)


class Department(models.Model):
    department_code = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    faculty = models.ForeignKey(Faculty, related_name='departments', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_contact'

    def __str__(self):  # __unicode__ on Python 2
        return self.__unicode__()

    def __unicode__(self):
        return '{} / {}'.format(self.name, self.faculty)

    @property
    def manager_role(self):
        return 'pk_{}.department_manager'.format(self.id)


class ContactRole(models.Model):
    """
    ContactRole Model
    """
    name = models.CharField(max_length=100, unique=True)

    e_research_body = models.ForeignKey(crams_models.EResearchBody, blank=True, null=True,
                                        related_name='contact_roles',
                                        default=None, on_delete=models.DO_NOTHING)

    project_leader = models.BooleanField(default=False)

    read_only = models.BooleanField(default=False)

    support_notification = models.BooleanField(default=False)

    class Meta:
        app_label = 'crams_contact'
        unique_together = ('name', 'e_research_body')

    def __str__(self):
        return '{}'.format(self.name)


class Contact(models.Model):
    """
    Contact Model
    """
    title = models.CharField(
        max_length=50, blank=True, null=True
    )

    given_name = models.CharField(
        max_length=200, blank=True, null=True
    )

    surname = models.CharField(
        max_length=200, blank=True, null=True
    )

    email = models.EmailField(unique=True, db_index=True)

    phone = models.CharField(
        max_length=50, blank=True, null=True
    )

    organisation = models.ForeignKey(Organisation,
                                     blank=True, null=True, on_delete=models.DO_NOTHING)

    orcid = models.URLField(blank=True, null=True,
                            validators=[validators.validate_orcid],
                            verbose_name='ORCID of contact')

    scopusid = models.CharField(
        max_length=50, blank=True, null=True
    )

    latest_contact = models.ForeignKey('Contact', blank=True, null=True, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_contact'

    def __str__(self):
        return '{0} {1} {2} {3}'.format(
            self.given_name, self.surname, self.title, self.pk)

    def get_full_name(self):
        def fmt(in_str):
            if in_str:
                return in_str + ' '
            return ''

        return fmt(self.title) + fmt(self.given_name) + fmt(self.surname)

    @property
    def system_identifiers(self):
        return EResearchContactIdentifier.objects.filter(
            contact=self, parent_erb_contact_id__isnull=True)

    @classmethod
    def fetch_contact_for_user(cls, user_obj):
        if isinstance(user_obj, crams_models.User):
            qs = Contact.objects.filter(
                email__iexact=user_obj.email, latest_contact__isnull=True)
            if qs.exists():
                return qs.first()
        return None

    def fetch_user_for_contact(self):
        return crams_models.User.objects.get(email=self.email)


class ContactDetail(models.Model):
    BUSINESS = 'B'
    MOBILE = 'M'
    PERSONAL = 'P'
    TYPE_CHOICES = ((BUSINESS, 'Business'), (PERSONAL, 'Personal'),
                    (MOBILE, 'Mobile'))
    type = models.CharField(
        max_length=1, choices=TYPE_CHOICES, default=PERSONAL)
    parent_contact = models.ForeignKey(Contact, related_name='contact_details', on_delete=models.DO_NOTHING)
    restricted = models.BooleanField(default=False)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        app_label = 'crams_contact'

    @classmethod
    def get_choice_value(cls, choice_str):
        if choice_str:
            for k, v in ContactDetail.TYPE_CHOICES:
                if choice_str.strip().capitalize() == v:
                    return k
        return None


class EResearchContactIdentifier(crams_models.ProvisionableItem):
    identifier = models.CharField(max_length=254)

    contact = models.ForeignKey(Contact, related_name='archive_contact_ids', on_delete=models.DO_NOTHING)

    system = models.ForeignKey(
        crams_models.EResearchBodyIDKey, related_name='contact_identifiers', on_delete=models.DO_NOTHING)

    parent_erb_contact_id = models.ForeignKey(
        'EResearchContactIdentifier', blank=True, null=True, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_contact'

    def __str__(self):
        return '{} / {} - {}'.format(
            self.identifier, self.contact, self.system)

    @classmethod
    def get_provider(cls):
        return None


class ContactLabel(crams_models.CramsCommon):
    label_name = models.CharField(max_length=255)

    active = models.BooleanField(default=True)

    contact = models.ForeignKey(Contact, related_name="labels", on_delete=models.CASCADE)

    class Meta:
        app_label = 'crams_contact'
        unique_together = ('label_name', 'contact')

    def __str__(self):
        return '{} / {}'.format(self.label_name, self.contact.get_full_name())


class CramsERBUserRoles(models.Model):
    contact = models.ForeignKey(Contact, related_name='user_roles', on_delete=models.DO_NOTHING)

    role_erb = models.ForeignKey(crams_models.EResearchBody, related_name='contacts', on_delete=models.DO_NOTHING)

    is_erb_admin = models.BooleanField(default=False)

    is_tenant_manager = models.BooleanField(default=False)

    delegates = models.ManyToManyField(
        crams_models.EResearchBodyDelegate, related_name='delegate_contacts')

    admin_erb_systems = models.ManyToManyField(
        crams_models.EResearchBodySystem, related_name='admin_contacts')

    approver_erb_systems = models.ManyToManyField(
        crams_models.EResearchBodySystem, related_name='approver_contacts')

    providers = models.ManyToManyField(
        crams_models.Provider, related_name='provider_contacts')

    end_date_ts = models.DateTimeField(blank=True, null=True)

    class Meta:
        app_label = 'crams_contact'
        unique_together = ('contact', 'role_erb', 'end_date_ts')

    def __str__(self):
        return self.contact.email

    @classmethod
    def query_current_roles(cls, contact_obj, erb_obj=None):
        qs_filter = models.Q(contact=contact_obj, end_date_ts__isnull=True)
        if erb_obj:
            qs_filter &= models.Q(role_erb=erb_obj)
        return CramsERBUserRoles.objects.filter(qs_filter)


class ContactLog(AbstractLinkToCramsLog):
    crams_contact_db_id = models.IntegerField(blank=True, null=True)

    class Meta:
        app_label = 'crams_contact'
        unique_together = ('crams_contact_db_id', 'log_parent')

    def __str__(self):
        return '{} {}'.format(self.log_parent, self.crams_contact_db_id)

    @classmethod
    def link_log(cls, log_obj, crams_contact_obj):
        if not isinstance(crams_contact_obj, Contact):
            exceptions.ValidationError('Contact object required to link to ContactLog')
        crams_contact_db_id = crams_contact_obj.id
        obj, _ = cls.objects.get_or_create(log_parent=log_obj, crams_contact_db_id=crams_contact_db_id)
        return obj

    @classmethod
    def fetch_log_qs(cls, crams_contact_db_id):
        return cls.objects.filter(crams_contact_db_id=crams_contact_db_id)
