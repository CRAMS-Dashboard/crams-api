# coding=utf-8
"""

"""
from rest_framework import permissions

from crams.extension import config_init
from crams_collection.permissions import IsProjectFacultyManager
from crams_allocation.models import RequestQuestionResponse
from crams_allocation.product_allocation.models import Request
from crams_collection.models import Project
from crams_allocation.product_allocation.models import StorageRequest
from crams.models import EResearchBodyDelegate
from crams.models import Question

from crams_allocation.utils.role import ProductRoleUtils

from django.conf import settings


class IsBatchIngestUser(permissions.IsAuthenticated):
    """
    Batch User validation. Only authenticated users with username specified
    in settings will be allowed to ingest
    """
    message = 'User does not have batch update privilege.'

    def has_permission(self, request, view):
        """
        User must be specfied in settings.BATCH_INGEST_USERS
        :param request:
        :param view:
        :return:
        """
        if super().has_permission(request, view):
            return request.user.username in settings.BATCH_INGEST_USERS
        return False


class IsFacultyManager(IsProjectFacultyManager):
    @classmethod
    def extract_project(cls, obj):
        project = super().extract_project(obj)
        if not project:
            if isinstance(obj, Request):
                project = obj.project
            elif isinstance(obj, StorageRequest):
                project = obj.request.project
        return project


# class IsAllocationContact(IsProjectContact):
#     """
#     Object-level permission to only allow reviewers of an object access to it.
#     """
#     @classmethod
#     def extract_project(cls, obj):
#         project = super().extract_project(obj)
#         if not project:
#             if isinstance(obj, Request):
#                 project = obj.project
#         return project


class IsRequestApprover(permissions.BasePermission):
    """
    Object-level permission to only allow Nectar approvers.
    """
    message = 'User does not hold Approver role for the Request.'

    def has_object_permission(self, http_request, view, obj):
        """
        User is an approver for given request's funding boby
        For a project object,
         - User must be an approver for every non-historic project request
        :param http_request:
        :param view:
        :param obj:
        :return:
        """
        def is_request_approver(request_obj):
            flat_roles = ProductRoleUtils.fetch_cramstoken_roles_flatten_to_list(
                http_request.user)

            required_role = request_obj.e_research_system.approver_role
            if required_role and required_role in flat_roles:
                return True

            return is_approver_delegate(request_obj, flat_roles)

        def is_approver_delegate(request_obj, user_roles_flat):
            erbs = request_obj.e_research_system
            # get question_key for delegate
            delegate_q_key = \
                config_init.DELEGATE_QUESTION_KEY_MAP.get(erbs.name)

            if delegate_q_key:
                q = Question.objects.get(key=delegate_q_key)
                for req_qr in RequestQuestionResponse.objects.filter(
                        question=q, request=request_obj).all():
                    for delegate in EResearchBodyDelegate.objects.filter(
                            e_research_body=erbs.e_research_body,
                            name=req_qr.question_response):
                        if delegate.approver_role in user_roles_flat:
                            return True
            return False

        if http_request.user:
            if isinstance(obj, Request):
                return is_request_approver(obj)
            if isinstance(obj, Project):
                requests = obj.requests
                for req in requests.filter(current_request__isnull=True):
                    if not is_request_approver(req):
                        return False
                return True

        return False
