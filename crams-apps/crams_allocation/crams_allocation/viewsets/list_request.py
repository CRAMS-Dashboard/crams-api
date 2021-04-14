# coding=utf-8
"""

"""
from rest_framework import response
from django.db.models import Prefetch

from crams.permissions import IsCramsAuthenticated
from crams.serializers import lookup_serializers
from crams_contact.serializers.contact_erb_roles import ContactErbRoleSerializer
from crams.serializers.lookup_serializers import UserSerializer
from crams_collection.viewsets.project_list_viewsets import ProjectListViewSet
from crams_collection.models import Project

from crams_allocation.product_allocation.models import Request
from crams_allocation.utils import request_utils
from crams_allocation.product_allocation.serializers.compute_request import ComputeRequestSerializer
from crams_allocation.product_allocation.serializers.storage_request_serializers import StorageRequestSerializer
from crams_allocation.serializers.question_serializers import RequestQuestionResponseSerializer
from crams_allocation.serializers.project_list import AllocationListProjectSerializer
from crams_allocation.serializers.project_request_serializers import ProjectRequestSerializer


class BaseProjectListViewset(ProjectListViewSet):
    @classmethod
    def populate_request_boolean(cls):
        # Override this method to return False, if no allocation related info is required
        return True

    @classmethod
    def optimise_project_qs(cls, project_qs):
        base_qs = project_qs.distinct().select_related('current_project')
        base_qs = base_qs.order_by('title', '-creation_ts')

        if cls.populate_request_boolean():
            request_prefetch = cls.optimise_request_qs(
                Request.objects.filter(current_request__isnull=True))
            return base_qs.prefetch_related(
                    Prefetch('requests', queryset=request_prefetch))

        return base_qs.prefetch_related(
            'requests__e_research_system__e_research_body',
            'requests__current_request',
            'requests__request_status',
            'requests__funding_scheme',
            'requests__storage_requests__storage_product',
            'requests__storage_requests__provision_details',
            'requests__compute_requests__compute_product',
            'requests__compute_requests__provision_details')

    @classmethod
    def optimise_request_qs(cls, request_qs, fetch_project_boolean=False):
        qs = request_qs.select_related(
            'current_request', 'request_status', 'funding_scheme',
            'e_research_system__e_research_body'
        ).prefetch_related('storage_requests__storage_product',
                           'storage_requests__provision_details',
                           'compute_requests__compute_product',
                           'compute_requests__provision_details'
                           )

        if not fetch_project_boolean:
            return qs

        qs = qs.select_related('project__current_project')
        return qs


class AllocationListViewset(BaseProjectListViewset):
    permission_classes = [IsCramsAuthenticated]
    queryset = Project.objects.none()
    serializer_class = AllocationListProjectSerializer

    @classmethod
    def get_list_serializer_class(cls):
        return cls.serializer_class

    @classmethod
    def get_detail_serializer_class(cls):
        return ProjectRequestSerializer

    @classmethod
    def build_view_response(cls, http_request, project_qs):
        if project_qs:
            erb_param = cls.get_eresearch_body_param(http_request)
            if erb_param:
                project_qs = project_qs.filter(
                    requests__e_research_system__e_research_body__name=erb_param,
                    requests__current_request__isnull=True
                )
            qs = cls.optimise_project_qs(project_qs)
            sz_class = cls.get_list_serializer_class()
            context = {'request': http_request}
            sz = sz_class(qs, many=True, context=context)
            return response.Response(sz.data)
        return response.Response([])


class ProjectRequestListViewSet(BaseProjectListViewset):
    """
    /project_request_list: <BR>
    list all projects linked to the current user <BR>
    /project_request_list/admin: <BR>
    list all projects the user is entitled to see as Crams Admin <BR>
    /project_request_list/faculty: <BR>
    list all projects the user is entitled to see as Faculty manager <BR>
    """
    permission_classes = [IsCramsAuthenticated]

    @classmethod
    def build_view_response(cls, http_request, project_qs):
        ret_dict = dict()
        ret_dict['user'] = UserSerializer(http_request.user).data

        if project_qs:
            qs = cls.optimise_project_qs(project_qs)
            ret_dict['projects'] = cls.populate_project_list_for_qs(qs, http_request.user)

        return response.Response(ret_dict)

    @classmethod
    def populate_project_list_for_qs(cls, project_objects, user_obj):
        """
        :param project_objects:
        :param user_obj:
        :return:
        """
        # fetch crams_token_dict once for repeated use in double loop below
        crams_token_dict = ContactErbRoleSerializer.fetch_cramstoken_roles_dict(user_obj)

        project_list = []
        for project in project_objects:
            project_dict = {}
            project_list.append(project_dict)
            project_dict['title'] = project.title
            project_dict['id'] = project.id
            if cls.populate_request_boolean():
                request_list = []
                project_dict['requests'] = request_list
                for cramsRequest in project.requests.all():
                    if cramsRequest.current_request:
                        continue  # historical request, ignore
                    request_list.append(cls.populate_request_data(
                        cramsRequest, user_obj, crams_token_dict))
        return project_list

    @classmethod
    def populate_request_data(cls, crams_request, user_obj, crams_token_dict):
        """
        populate_request_data
        :param crams_request:
        :param user_obj:
        :param crams_token_dict:
        :return:
        """
        request_dict = dict()
        request_dict['id'] = crams_request.id
        request_dict['request_status'] = request_utils.get_erb_request_status_dict(crams_request)
        request_dict['expiry'] = crams_request.end_date
        if crams_request.funding_scheme:
            request_dict['funding'] = crams_request.funding_scheme.funding_scheme
        if crams_request.e_research_system:
            request_dict['e_research_system'] = \
                lookup_serializers.EResearchSystemSerializer(
                    crams_request.e_research_system).data

        request_dict['national_percent'] = crams_request.national_percent
        request_dict['transaction_id'] = crams_request.transaction_id
        request_dict['allocation_home'] = None
        if crams_request.allocation_home:
            request_dict['allocation_home'] = crams_request.allocation_home.code

        fn = request_utils.BaseRequestUtils.get_restricted_updated_by
        request_dict['updated_by'] = fn(crams_request, crams_token_dict)

        compute_list = []
        request_dict['compute_requests'] = compute_list
        pd_context = ComputeRequestSerializer.build_context_obj(
            user_obj, crams_request.e_research_system)

        for compute_request in crams_request.compute_requests.all():
            serializer = ComputeRequestSerializer(compute_request,
                                                  context=pd_context)
            compute_data = serializer.data
            compute_list.append(compute_data)
            # override id value to name value
            compute_data['compute_product'] = {
                'id': compute_request.compute_product.id,
                'name': compute_request.compute_product.name
            }

        storage_list = []
        request_dict['storage_requests'] = storage_list
        pd_context = StorageRequestSerializer.build_context_obj(
            user_obj, crams_request.e_research_system)

        for storage_request in crams_request.storage_requests.all():
            serializer = StorageRequestSerializer(storage_request,
                                                  context=pd_context)
            storage_data = serializer.data
            storage_list.append(storage_data)
            # override id value to name value
            storage_data['storage_product'] = {
                'id': storage_request.storage_product.id,
                'name': storage_request.storage_product.name
            }
            # add parent_storage_product_id if exists
            storage_product = storage_request.storage_product
            if storage_product.parent_storage_product:
                storage_data['storage_product']['parent_storage_product'] = {
                    'id': storage_product.parent_storage_product.id,
                    'name': storage_product.parent_storage_product.name
                }
            else:
                storage_data['storage_product']['parent_storage_product'] = None

        request_question_responses = []
        request_dict['request_question_responses'] = request_question_responses
        for rqr in crams_request.request_question_responses.all():
            rqr_data = RequestQuestionResponseSerializer(rqr).data
            request_question_responses.append(rqr_data)

        return request_dict
