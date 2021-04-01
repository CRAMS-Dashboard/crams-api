from django.db import models
from crams import models as crams_model
from crams_contact import models as contact_models


class ServiceManager(models.Model):
    contact = models.OneToOneField(contact_models.Contact, unique=True)

    active = models.BooleanField(default=True)

    class Meta(object):
        app_label = 'manager'

    def __str__(self):
        return '{}'.format(self.contact)

    @property
    def manager_role(self):
        return 'service_manager'


class FacultyManager(models.Model):
    contact = models.ForeignKey(
        contact_models.Contact, related_name='manager_faculties')

    faculty = models.ForeignKey(
        crams_model.Faculty, related_name='faculty_managers')

    active = models.BooleanField(default=True)

    class Meta(object):
        app_label = 'manager'
        unique_together = ('contact', 'faculty')

    def __str__(self):
        return '{} - {}'.format(self.contact, self.faculty)


class DepartmentManager(models.Model):
    contact = models.ForeignKey(
        contact_models.Contact, related_name='manager_departments')

    department = models.ForeignKey(
        crams_model.Department, related_name='department_managers')

    active = models.BooleanField(default=True)

    class Meta(object):
        app_label = 'manager'
        unique_together = ('contact', 'department')

    def __str__(self):
        return '{} - {}'.format(self.contact, self.department)


class OrganisationManager(models.Model):
    contact = models.ForeignKey(
        contact_models.Contact, related_name='manager_organisations')

    organisation = models.ForeignKey(
        crams_model.Organisation, related_name='organisation_managers')

    active = models.BooleanField(default=True)

    class Meta(object):
        app_label = 'manager'
        unique_together = ('contact', 'organisation')

    def __str__(self):
        return '{} - {}'.format(self.contact, self.organisation)

