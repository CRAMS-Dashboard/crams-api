# coding=utf-8
"""

"""
from rest_framework import permissions
from crams import permissions as crams_permissions
from crams.utils import role
from crams.models import Question, EResearchBodyDelegate
from crams_allocation.models import Request, RequestQuestionResponse
from crams_allocation.config.allocation_config import DELEGATE_QUESTION_KEY_MAP
from crams_collection.models import Project
from crams_allocation.storage.models import StorageRequest


class IsFacultyManager(crams_permissions.IsAbstractFacultyManager):
    @classmethod
    def has_access_to_obj(cls, user, obj):
        role_exists, user_roles_dict = cls.user_roles_common(user)
        if not role_exists:
            return False

        project = None
        if isinstance(obj, Project):
            project = obj
        elif isinstance(obj, Request):
            project = obj.project
        elif isinstance(obj, StorageRequest):
            project = obj.request.project

        if not project:
            return False

        faculty_roles = user_roles_dict[role.AbstractCramsRoleUtils.FACULTY_MANAGEMENT_ROLE_TYPE]
        if project.department:
            return project.department.faculty.manager_role in faculty_roles
        return False


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
            flat_roles = role.AbstractCramsRoleUtils.fetch_cramstoken_roles_flatten_to_list(
                http_request.user)

            required_role = request_obj.e_research_system.approver_role
            if required_role and required_role in flat_roles:
                return True

            return is_approver_delegate(request_obj, flat_roles)

        def is_approver_delegate(request_obj, user_roles_flat):
            erbs = request_obj.e_research_system
            # get question_key for delegate
            delegate_q_key = DELEGATE_QUESTION_KEY_MAP.get(erbs.name)

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


class IsProjectContact(permissions.BasePermission):
    """
    Object-level permission to only allow reviewers of an object access to it.
    """

    message = 'User is not listed as contact for the relevant project.'

    @classmethod
    def common_object_permission(cls, http_request_obj, obj):
        """
        for use by this permission and other friendly classes
        :param http_request_obj:
        :param obj:
        :return:
        """
        project = None
        if isinstance(obj, Project):
            project = obj
        elif isinstance(obj, Request):
            project = obj.project

        if not project:
            return False

        return project.project_contacts.filter(
            contact__email__iexact=http_request_obj.user.email).exists()

    def has_object_permission(self, request, view, obj):
        """
            User has permission to view given project or request object
        :param request:
        :param view:
        :param obj:
        :return:
        """
        return self.common_object_permission(request, obj)
