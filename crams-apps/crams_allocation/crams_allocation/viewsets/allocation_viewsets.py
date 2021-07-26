# coding=utf-8
"""
    views
"""
from crams.permissions import IsCramsAuthenticated
from crams_collection.models import Project
from crams_collection.permissions import IsProjectContact
from crams_collection.utils.crams_rest_request_util import CramsRestRequestData
from django.core import exceptions
from django.db.models import Q
from rest_condition import And, Or
from rest_framework import exceptions as rest_exceptions

from crams_collection.viewsets.project_viewsets import AbstractProjectViewSet
from crams_allocation.models import Request
from crams_allocation.permissions import IsRequestApprover
from crams_allocation.serializers.project_request_serializers import ProjectRequestSerializer
from crams_allocation.utils import project_request_utils


class AbstractProjectRequestViewSet(AbstractProjectViewSet):
    def __init__(self, **kwargs):
        self.crams_object_level = False
        super().__init__(**kwargs)

    def get_object(self):
        self.crams_object_level = True
        return super().get_object()

    @classmethod
    def validate_allocation_permission(cls, request_id, user_obj, contact_obj):
        return project_request_utils.validate_user_permission_for_request_id(
            request_id, user_obj, contact=contact_obj)

    def get_request_contact_filter(self, data):
        # list filter
        p_ids = data.contact.project_contacts.values_list(
            'project', flat=True)
        q_obj = Q(project__id__in=p_ids)
        if not self.crams_object_level:
            q_obj = q_obj & Q(current_request__isnull=True,
                              project__current_project__isnull=True)
        return q_obj

    def get_project_request_id_filter(self, data):
        if data.request_id:
            request = self.validate_allocation_permission(
                data.request_id, data.user, contact_obj=data.contact)
            return Q(pk=request.project.id)

        if data.pk:
            project = Project.objects.get(pk=data.pk)
            for request in project.requests.all():
                # Ensure all requests in project are valid for user
                self.validate_allocation_permission(
                    request.id, data.user, contact_obj=data.contact)
            return Q(id=data.pk)

        raise rest_exceptions.PermissionDenied(
            detail="Neither project nor request id was provided!!!!")

    def get_project_crams_id_filter(self, data):
        p_filter = super().get_project_crams_id_filter(data)
        projects = Project.objects.filter(p_filter)
        if projects.exists():
            request_id = None
            for p in projects:
                if p.requests.exists():
                    non_current_requests = p.requests
                    request_id = non_current_requests.first().id
                current_requests = p.requests.filter(current_request__isnull=True)
                if current_requests.exists():
                    request_id = current_requests.first().id
                    break
            if request_id:
                request = self.validate_allocation_permission(
                    request_id, data.user, contact_obj=data.contact)
                return Q(pk=request.project.id)
            raise rest_exceptions.PermissionDenied(
                detail="No valid requests available for given crams project id!!!!")

    def get_queryset(self):
        def get_request_id_filter(data_obj):
            if data_obj.pk and data_obj.request_id:
                raise exceptions.ValidationError(
                    'request_id param not valid for Request object fetch')

            request_id = data_obj.request_id or data_obj.pk
            if not request_id:
                raise rest_exceptions.PermissionDenied('Request id expected')
            # check contact permissions to access request
            request = self.validate_allocation_permission(
                request_id, data_obj.user, contact_obj=data_obj.contact)
            if request:
                return Q(pk=request.id)

            raise rest_exceptions.PermissionDenied()

        queryset = self.queryset
        qs_filter = Q(id__isnull=True)  # exclude everything by default

        data = CramsRestRequestData(self)
        if data.request_id or self.crams_object_level:
            if queryset.model is Project:
                qs_filter = self.get_project_request_id_filter(data)
            elif queryset.model is Request:
                qs_filter = get_request_id_filter(data)

            if not queryset.filter(qs_filter).exists():
                raise exceptions.PermissionDenied()
        else:
            if data.crams_id:
                qs_filter = self.get_project_crams_id_filter(data)
            else:
                if queryset.model is Project:
                    qs_filter = self.get_project_contact_filter(data)
                elif queryset.model is Request:
                    qs_filter = self.get_request_contact_filter(data)

        return queryset.filter(qs_filter).distinct()


class ProjectRequestViewSet(AbstractProjectRequestViewSet):
    """
    /project_request_list: <BR>
    list all projects (with metadata and allocation information) linked to the current user <BR>
    /project_request_list/admin: <BR>
    list all projects (with metadata and allocation information) the user is entitled to see as Crams Admin <BR>
    /project_request_list/faculty: <BR>
    list all projects (with metadata and allocation information) the user is entitled to see as Faculty manager <BR>
    """
    permission_classes = [IsCramsAuthenticated]    # Project level access is checked in the list view
    queryset = Project.objects.all()
    serializer_class = ProjectRequestSerializer
    ordering_fields = ('project', 'creation_ts')
    ordering = ('project', '-creation_ts')

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            'created_by', 'updated_by', 'current_project').prefetch_related(
            'project_question_responses__question',
            'project_contacts__contact__organisation',
            'project_contacts__contact__contact_details',
            'project_contacts__contact_role',
            'project_contacts__contact__archive_contact_ids',
            'archive_project_ids',
            'linked_provisiondetails__provision_details',
            'requests__request_question_responses__question',
            'requests__storage_requests__provision_id',
            'requests__storage_requests__storage_product__provider',
            'requests__storage_requests__storage_product__storage_type',
            'requests__storage_requests__provision_details',
            'requests__storage_requests__storage_question_responses__question',
            'requests__compute_requests__compute_product__provider',
            'requests__compute_requests__provision_details',
            'requests__compute_requests__compute_question_responses__question',
            'requests__e_research_system__e_research_body',
            'requests__funding_scheme__funding_body',
            'requests__request_status',
            'requests__history',
            'requests__updated_by',
            'requests__created_by',
            'requests__current_request',
            'department__faculty__organisation',
            'grants__grant_type',
            'domains__for_code'
        )


# class ProjectViewSet(AbstractProjectRequestViewSet, AbstractProjectViewset):
#     """
#     class ProjectViewSet
#     """
#     permission_classes = [IsCramsAuthenticated]
#     queryset = Project.objects.all()
#     serializer_class = ProjectSerializer
#     ordering_fields = ('title', 'creation_ts')
#     ordering = ('title', '-creation_ts')
#
#     def get_queryset(self):
#         qs = super().get_queryset()
#         return qs.select_related(
#             'created_by', 'updated_by', 'current_project').prefetch_related(
#             'project_question_responses__question',
#             'project_contacts__contact__organisation',
#             'project_contacts__contact__contact_details',
#             'project_contacts__contact_role',
#             'project_contacts__contact__archive_contact_ids',
#             'archive_project_ids',
#             'linked_provisiondetails__provision_details',
#             'requests__request_question_responses__question',
#             'requests__storage_requests__provision_id',
#             'requests__storage_requests__storage_product__provider',
#             'requests__storage_requests__storage_product__storage_type',
#             'requests__storage_requests__provision_details',
#             'requests__storage_requests__storage_question_responses__question',
#             'requests__compute_requests__compute_product__provider',
#             'requests__compute_requests__provision_details',
#             'requests__compute_requests__compute_question_responses__question',
#             'requests__e_research_system__e_research_body',
#             'requests__funding_scheme__funding_body',
#             'requests__request_status',
#             'requests__history',
#             'requests__updated_by',
#             'requests__created_by',
#             'requests__current_request',
#             'department__faculty__organisation',
#             'grants__grant_type',
#             'domains__for_code'
#         )
