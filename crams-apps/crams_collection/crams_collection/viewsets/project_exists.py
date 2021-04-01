# coding=utf-8
"""

"""
from crams.permissions import IsCramsAuthenticated
from rest_framework import viewsets, decorators
from rest_framework.views import Response

from crams_collection.models import ProjectID, EResearchBodyIDKey


class ProjectExistsViewset(viewsets.ViewSet):
    """
    /exists/project usage:
    Check if project meta data exists for erb or erbs
    e.g:
    exists/project/?erb=<erb_name>&project_title=<project_title>
    exists/project/?erbs=<erbs_name>&project_title=<project_title>
    """
    serializer_class = None
    permission_classes = [IsCramsAuthenticated]
    queryset = ProjectID.objects.none()

    @decorators.action(detail=False,
                       url_path='project_id/(?P<system_pk>\d+)/(?P<project_id>\S+)', url_name='id-exists')
    def projectid_exists_for_system(self, request, system_pk, project_id):
        ret_dict = {
            'exists': False,
            'message': None
        }
        try:
            system = EResearchBodyIDKey.objects.get(pk=system_pk)
            if project_id is not None:
                qs = ProjectID.objects.filter(
                    system=system, identifier__iexact=project_id)
                ret_dict['exists'] = qs.exists()
        except EResearchBodyIDKey.DoesNotExist:
            ret_dict['message'] = \
                'System DB id {}: does not exists'.format(system_pk)

        return Response(ret_dict)
