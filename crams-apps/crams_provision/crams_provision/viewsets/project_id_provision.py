# coding=utf-8
"""

"""
from crams.models import ProvisionDetails
from crams.permissions import IsCramsAuthenticated
from crams_collection.models import Project, ProjectID
from django.db.models import Q
from rest_framework import decorators, exceptions
from rest_framework.response import Response

from crams_provision.serializers import projectid_contact_provision
from crams_provision.viewsets.base import ProvisionCommonViewSet


class ProjectIDProvisionViewSet(ProvisionCommonViewSet):
    permission_classes = [IsCramsAuthenticated]
    queryset = ProjectID.objects.none()
    serializer_class = projectid_contact_provision.ProvisionProjectIDUtils

    @decorators.action(detail=False, methods=['get'], url_path='members')
    def project_members(self, request, *args, **kwargs):
        sz_class = projectid_contact_provision.ProjectMemberContactIDList
        erb_obj = self.fetch_e_research_body_param_obj()

        valid_erb_list = self.get_user_provision_erbs(
            self.get_current_user(), erb_obj)
        if valid_erb_list:
            qs = Project.objects.filter(
                current_project__isnull=True,
                requests__e_research_system__e_research_body__in=valid_erb_list
            ).distinct()

            context = {'valid_erb_list': valid_erb_list}
            system_obj = self.fetch_system_key_param_obj(erb_obj)
            if system_obj:
                context['system_obj'] = system_obj
            return Response(sz_class(qs, many=True, context=context).data)

        msg = 'User does not have required Provider privileges'
        if erb_obj:
            msg = msg + ' for {}'.format(erb_obj.name)
        raise exceptions.ValidationError(msg)

    def get_queryset(self):
        required_status = ProvisionDetails.SET_OF_SENT
        id_filter = Q(provision_details__isnull=True) | Q(
            provision_details__status__in=required_status)
        id_filter &= Q(parent_erb_project_id__isnull=True)
        id_filter &= Q(project__current_project__isnull=True)

        return ProjectID.objects.filter(id_filter)

    def list(self, request, *args, **kwargs):
        erb_obj = self.fetch_e_research_body_param_obj()

        valid_erb_list = self.get_user_provision_erbs(
            self.get_current_user(), erb_obj)
        if valid_erb_list:
            qs = self.get_queryset().filter(
                system__e_research_body__in=valid_erb_list)
            return Response(self.serializer_class.
                            build_project_id_list_json(qs))

        msg = 'User does not have required Provider privileges'
        if erb_obj:
            msg = msg + ' for {}'.format(erb_obj.name)
        raise exceptions.ValidationError(msg)

    @decorators.action(detail=False, methods=['post'], url_path='update')
    def update_provision(self, request, *args, **kwargs):
        ret_data = self.update_provision_data_input(
            request.data, self.get_current_user())
        return Response(ret_data)

    @classmethod
    def update_provision_data_input(cls, data, current_user):
        id_key = 'project_ids'
        sz_class = projectid_contact_provision.ProvisionProjectIDUtils
        project_id_data_list = \
            sz_class.validate_project_identifiers_in_project_list(
                data, current_user, id_key)

        id_obj_list = sz_class.update_project_data_list(
            id_key, project_id_data_list)

        ret_data = sz_class.build_project_id_list_json(id_obj_list)
        return ret_data
