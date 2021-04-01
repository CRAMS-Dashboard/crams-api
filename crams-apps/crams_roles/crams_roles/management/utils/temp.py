# coding=utf-8
"""

"""
from django.db.models import Q
from rest_framework import exceptions

from crams import models as crams_models
from crams_roles.management import models as manager_models


def fetch_contact_organisation_qs(contact):
    org_pk_set = set()
    for org_manager in contact.manager_organisations.filter(active=True):
        org_pk_set.add(org_manager.organisation.id)
    return crams_models.Organisation.objects.filter(pk__in=org_pk_set)


def fetch_contact_faculties_qs(contact):
    faculty_pk_set = set()
    for erb_user_role in contact.manager_faculties.filter(active=True):
        faculty_pk_set.add(erb_user_role.faculty.id)

    org_qs = fetch_contact_organisation_qs(contact)

    qs_filter = Q(organisation__in=org_qs) | Q(pk__in=faculty_pk_set)
    return crams_models.Faculty.objects.filter(qs_filter)


def fetch_contact_departments_qs(contact):
    pk_set = set()
    qs_all = manager_models.DepartmentManager.objects
    for department_manager in qs_all.filter(active=True, contact=contact):
        pk_set.add(department_manager.department.id)

    faculty_qs = fetch_contact_faculties_qs(contact)

    qs_filter = Q(faculty__in=faculty_qs) | Q(pk__in=pk_set)
    return crams_models.Department.objects.filter(qs_filter)
