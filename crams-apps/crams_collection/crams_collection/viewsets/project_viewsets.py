from crams.permissions import IsCramsAuthenticated
from crams.utils.django_utils import CramsModelViewSet
from django.db.models import Q
from rest_framework import exceptions as rest_exceptions

from crams_collection.models import Project
from crams_collection.serializers.project_serializer import ProjectSerializer
from crams_collection.utils.crams_rest_request_util import CramsRestRequestData
from crams_collection.utils.project_role_querysets import DefaultProjectRoleQueryset


class AbstractProjectViewSet(DefaultProjectRoleQueryset, CramsModelViewSet):
    def __init__(self, **kwargs):
        self.crams_object_level = False
        super().__init__(**kwargs)

    def get_object(self):
        self.crams_object_level = True
        return super().get_object()

    def get_project_contact_filter(self, http_request_data):
        # list filter
        q_obj = http_request_data.contact.project_contacts.all()
        if not self.crams_object_level:
            q_obj = q_obj.filter(project__current_project__isnull=True)
        return Q(id__in=q_obj.values_list('project', flat=True))

    def get_project_id_filter(self, http_request_data):
        if http_request_data.pk:
            if len(http_request_data.user_erb_list) > 0:
                return Q(id=http_request_data.pk)
            return self.get_project_contact_filter(http_request_data)

        raise rest_exceptions.PermissionDenied(
            detail="project id was provided!!!!")

    def get_project_crams_id_filter(self, request_data):
        if request_data.crams_id:
            try:
                projects = Project.objects.filter(
                    Q(crams_id=request_data.crams_id, current_project=None))
                if projects.exists():
                    return Q(pk=projects.first().pk)
            except:
                raise rest_exceptions.PermissionDenied()

    def get_queryset(self):
        queryset = self.queryset
        if not queryset.model is Project:
            raise rest_exceptions.APIException('Invalid object passed to AbstractProjectViewSet')

        rest_request_data = CramsRestRequestData(self)
        if self.crams_object_level:
            qs_filter = self.get_project_id_filter(rest_request_data)
            if not queryset.filter(qs_filter).exists():
                raise rest_exceptions.PermissionDenied()
        else:
            if rest_request_data.crams_id:
                qs_filter = self.get_project_crams_id_filter(rest_request_data)
            else:
                qs_filter = self.get_project_contact_filter(rest_request_data)

        return queryset.filter(qs_filter).distinct()


class ProjectViewSet(AbstractProjectViewSet):
    """
    /project_request_list: <BR>
    list all projects (with project metadata at collection level) linked to the current user <BR>
    /project_request_list/admin: <BR>
    list all projects (with project metadata at collection level) the user is entitled to see as Crams Admin <BR>
    /project_request_list/faculty: <BR>
    list all projects (with project metadata only at collection level) the user is entitled to see as Faculty manager <BR>
    """
    permission_classes = [IsCramsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    ordering_fields = ('title', 'creation_ts')
    ordering = ('title', '-creation_ts')

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
            'department__faculty__organisation',
            'grants__grant_type',
            'domains__for_code'
        )
