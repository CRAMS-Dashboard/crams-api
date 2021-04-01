# coding=utf-8
"""

"""
import copy
from django.db import models
from rest_framework import serializers, exceptions as rest_exceptions

from crams import permissions
from crams.utils import model_lookup_utils
from crams_allocation.permissions import IsFacultyManager
from crams_contact.utils import contact_utils
from crams_allocation.config import allocation_config
from crams_collection.models import ProjectContact, Project
from crams_allocation.models import Request


def extract_project_id_save_args(project_id_data):
    ret_dict = copy.deepcopy(project_id_data)

    system_data = project_id_data.get('system')
    if not system_data:
        raise serializers.ValidationError(
            'Project Id ({}): System details is required'.format(
                project_id_data.get('identifier')))

    if not isinstance(system_data, dict):
        if isinstance(system_data, int):
            system_data = {
                'id': system_data
            }
        else:
            system_data = {
                'key': str(system_data)
            }
    try:
        ret_dict['system_obj'] = model_lookup_utils.get_system_obj(system_data)
    except rest_exceptions.ParseError as e:
        raise serializers.ValidationError('Project Id ({}): {}'.format(
            ret_dict['identifier'], repr(e)))

    return ret_dict


def validate_user_permission_for_request_id(request_id, user, contact=None):
    # bypass if no request id
    if not request_id:
        raise rest_exceptions.PermissionDenied('Request id expected')

    contact = contact or contact_utils.fetch_user_contact_if_exists(user)
    if not contact:
        raise rest_exceptions.ValidationError('Contact expected')

    request = Request.objects.get(pk=request_id)

    prj_cont = ProjectContact.objects.filter(
        contact=contact, project=request.project)

    # ignore if user is a project contact for this request
    if prj_cont.exists():
        return request

    # check if request is historical & user is current project contact
    if request.current_request:
        current_project = request.current_request.project
        if current_project.project_contacts.filter(
                contact=contact).exists():
            return request

    # permit if user is ServiceManager
    if permissions.IsServiceManager.role_exists_for_user(user):
        return request

    # permit if user is a Faculty manager for Project department
    if IsFacultyManager.has_access_to_obj(user, request):
        return request

    # permit if user is approver for request
    req_erb_system = request.e_research_system
    req_erb = req_erb_system.e_research_body
    for erb_role in contact.user_roles.filter(role_erb=req_erb):
        # ERB Admin
        if erb_role.is_erb_admin:
            return request
        # ERB System Admin
        if req_erb_system in erb_role.admin_erb_systems.all():
            return request

        key = allocation_config.DELEGATE_QUESTION_KEY_MAP.get(
            req_erb_system.name)
        if key:
            if erb_role.delegates.exists():
                rq_qs = request.request_question_responses
                for rq in rq_qs.filter(question__key=key):
                    delegate_name = rq.question_response
                    if erb_role.delegates.filter(
                            name=delegate_name).exists():
                        return request
            msg = 'Delegate roles not defined for {}'.format(key)
            raise rest_exceptions.ValidationError(msg)

        elif req_erb_system in erb_role.approver_erb_systems.all():
            return request

    raise rest_exceptions.PermissionDenied(
        detail="User does not have access to this request!!!!")


def get_archive_project_qs(project, include_current_project=False):
    if project and isinstance(project, Project):
        parent_project = project
        if project.current_project:
            parent_project = project.current_project
        base_qs = Project.objects.filter(current_project=parent_project)
        qs_filter = models.Q(creation_ts__lte=project.creation_ts)
        if include_current_project:
            qs_filter |= models.Q(id=parent_project.id)
        return base_qs.filter(qs_filter)

    return Project.objects.none()
