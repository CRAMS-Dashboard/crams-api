# coding=utf-8
"""

"""

from django.db.models import Q

from crams_collection.models import Project
from crams_collection.utils import project_user_utils


class DefaultProjectRoleQueryset:
    @classmethod
    def optimise_project_qs(cls, project_qs):
        base_qs = project_qs.select_related('current_project')

        return base_qs.prefetch_related(
            'project_contacts__contact',
            'project_contacts__contact_role',
            'project_ids__system__e_research_body',
            'domains',
            'publications',
            'grants')

    @classmethod
    def build_null_role_queryset(cls, qs, contact):
        qs = Project.objects.none()
        if contact:
            qs = Project.objects.filter(
                current_project__isnull=True,
                project_contacts__contact=contact)

        return qs

    @classmethod
    def build_admin_queryset(cls, qs, erbs_list):
        qs = Project.objects.none()
        if erbs_list:
            qs = Project.objects.filter(current_project__isnull=True)
        return qs

    @classmethod
    def build_faculty_queryset(cls, qs, contact):
        qs = Project.objects.none()
        if contact:
            faculty_qs = project_user_utils.fetch_contact_faculties_qs(contact)
            qs = Project.objects.filter(
                current_project__isnull=True,
                department__faculty__in=faculty_qs)

        return qs

    @classmethod
    def build_department_queryset(cls, qs, contact):
        qs = Project.objects.none()
        if contact:
            department_qs = project_user_utils.fetch_contact_departments_qs(contact)
            qs = Project.objects.filter(
                current_project__isnull=True, department__in=department_qs)

        return qs

    @classmethod
    def build_organisation_queryset(cls, qs, contact):
        qs = Project.objects.none()
        if contact:
            org_qs = project_user_utils.fetch_contact_organisation_qs(contact)
            qs = Project.objects.filter(
                current_project__isnull=True,
                department__faculty__organisation__in=org_qs)

        return qs

    @classmethod
    def build_archive_project_queryset(cls, project_qs):
        project_ids = project_qs.values_list('id', flat=True)
        filter_qs = Q(id__in=project_ids) | Q(current_project__in=project_ids)
        return Project.objects.filter(filter_qs)
