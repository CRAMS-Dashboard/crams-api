# coding=utf-8
"""

"""
from crams.permissions import IsCramsAuthenticated
from django.db.models import Q
from rest_framework import viewsets, decorators
from rest_framework.exceptions import ParseError
from rest_framework.views import Response

from crams_collection.models import ProjectID
from crams_allocation.models import Request


class AllocationExistsViewset(viewsets.ViewSet):
    """
    /exists/project usage: <BR>
    Check if project meta data exists for erb or erbs <BR>
    e.g: <BR>
    exists/project/?erb=<erb_name>&project_title=<project_title> <BR>
    exists/project/?erbs=<erbs_name>&project_title=<project_title> <BR>
    """
    serializer_class = None
    # permission_classes = [IsCramsAuthenticated]
    queryset = ProjectID.objects.none()

    @decorators.action(detail=False, url_path='project', url_name='title-exists')
    def project_meta_data_exists(self, request):
        prj_id = request.query_params.get('project_id')
        erb_name = request.query_params.get('erb')
        erbs_name = request.query_params.get('erbs')
        title = request.query_params.get('title')
        if erb_name and erbs_name:
            raise ParseError(
                'Can not query both erb and erbs at the a time')
        if not title:
            raise ParseError(
                'Need title param in order to query')
        q_conditions = Q(project__title__icontains=title)
        # check the project title in erb
        if erb_name:
            q_conditions.add(Q(e_research_system__e_research_body__name__iexact=erb_name), Q.AND)
        # check the project title in erbs
        if erbs_name:
            q_conditions.add(Q(e_research_body_system__name__iexact=erbs_name), Q.AND)
        # check the project
        if prj_id:
            proj_conditions = Q(project__id=prj_id) | Q(project__current_project__id=prj_id)
            q_conditions.add(proj_conditions, Q.AND)
            project_queryset = Request.objects.filter(q_conditions)
            # ignore the project id if found, as it's current project
            if project_queryset:
                return Response(False)

        # do final query to check project title exists or not
        queryset = Request.objects.filter(q_conditions)
        # if found return true
        if queryset:
            return Response(True)
        # else not found return false
        return Response(False)
