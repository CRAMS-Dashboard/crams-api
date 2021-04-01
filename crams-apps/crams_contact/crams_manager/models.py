from django.db import models
from crams_contact import models as contact_model


class ServiceManager(models.Model):
    contact = models.OneToOneField(contact_model.Contact, unique=True, on_delete=models.DO_NOTHING)

    active = models.BooleanField(default=True)

    class Meta(object):
        app_label = 'crams_manager'

    def __str__(self):
        return '{}'.format(self.contact)

    @property
    def manager_role(self):
        return 'service_manager'


class FacultyManager(models.Model):
    contact = models.ForeignKey(
        contact_model.Contact, related_name='manager_faculties', on_delete=models.DO_NOTHING)

    faculty = models.ForeignKey(
        contact_model.Faculty, related_name='faculty_managers', on_delete=models.DO_NOTHING)

    active = models.BooleanField(default=True)

    class Meta(object):
        app_label = 'crams_manager'
        unique_together = ('contact', 'faculty')

    def __str__(self):
        return '{} - {}'.format(self.contact, self.faculty)


class DepartmentManager(models.Model):
    contact = models.ForeignKey(
        contact_model.Contact, related_name='manager_departments', on_delete=models.DO_NOTHING)

    department = models.ForeignKey(
        contact_model.Department, related_name='department_managers', on_delete=models.DO_NOTHING)

    active = models.BooleanField(default=True)

    class Meta(object):
        app_label = 'crams_manager'
        unique_together = ('contact', 'department')

    def __str__(self):
        return '{} - {}'.format(self.contact, self.department)


class OrganisationManager(models.Model):
    contact = models.ForeignKey(
        contact_model.Contact, related_name='manager_organisations', on_delete=models.DO_NOTHING)

    organisation = models.ForeignKey(
        contact_model.Organisation, related_name='organisation_managers', on_delete=models.DO_NOTHING)

    active = models.BooleanField(default=True)

    class Meta(object):
        app_label = 'crams_manager'
        unique_together = ('contact', 'organisation')

    def __str__(self):
        return '{} - {}'.format(self.contact, self.organisation)
