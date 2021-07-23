# coding=utf-8
"""

"""

import datetime
from collections import OrderedDict

from crams.constants import db
from crams.extension import config_init
from crams.models import Question
from crams.serializers import lookup_serializers
from crams.serializers.lookup_serializers import UserSerializer
from crams.utils import lang_utils
from crams_contact.models import Contact
from crams_contact.serializers.contact_erb_roles import ContactErbRoleSerializer
from crams_contact.utils import contact_utils
from django.db.models import Q
from rest_framework.response import Response

from crams_allocation.constants import api
from crams_allocation.models import Request
from crams_allocation.models import RequestQuestionResponse
from crams_allocation.product_allocation.serializers.compute_request import ComputeRequestSerializer
from crams_allocation.product_allocation.serializers.storage_request_serializers import StorageRequestSerializer
from crams_allocation.serializers.product_request import AllocationProvisionDetailsSerializer
from crams_allocation.serializers.question_serializers import RequestQuestionResponseSerializer
from crams_allocation.utils import request_utils
from crams_allocation.utils.request_utils import BaseRequestUtils
from crams_allocation.utils.role import ProductRoleUtils


def get_e_research_systems_for_request_user(http_request):
    erb_system_list = ContactErbRoleSerializer.get_authorised_e_research_system_list(http_request.user, debug=True)
    request_e_system = http_request.query_params.get('e_research_system_name')
    if request_e_system:
        ret_list = list()
        for erb_system in erb_system_list:
            if lang_utils.strip_lower(erb_system.name) == \
                    lang_utils.strip_lower(request_e_system):
                ret_list.append(erb_system)
        return ret_list

    return erb_system_list


def get_request_status_count(e_research_systems):
    def counter_fn(request_status):
        qs = fetch_current_requests_for_status(
            request_status, e_research_systems)

        return qs.count()

    ret_dict = dict()
    ret_dict['counter'] = {
        'new': counter_fn(api.REQ_NEW),
        'approved': counter_fn(api.REQ_APPROVED),
        'active': counter_fn(api.REQ_ACTIVE),
        'expired': counter_fn(api.REQ_EXPIRY)
    }
    return ret_dict


def query_projects(http_request, e_research_systems, req_status):
    """

    :param http_request:
    :param e_research_systems:
    :param req_status:
    :return:
    """
    contact = Contact.objects.get(email=http_request.user.email)
    user_delegates = contact_utils.fetch_contact_delegates_for_erb_systems(
        contact, e_research_systems)
    valid_delegate_names = set()
    for ud in user_delegates:
        valid_delegate_names.add(lang_utils.strip_lower(ud.name))

    if req_status == api.REQ_ACTIVE:
        provider_erb_systems = ProductRoleUtils.get_provider_erbs_for_user(user_obj=http_request.user)
        e_research_systems = set(e_research_systems + provider_erb_systems)

    request_qs = fetch_current_requests_for_status(req_status, e_research_systems)

    projects_dict = OrderedDict()
    filter_by_delegate_status = [api.REQ_ACTIVE]
    for crams_request in request_qs:
        # get the question_key for delegate if any
        del_key = config_init.DELEGATE_QUESTION_KEY_MAP.get(
            crams_request.e_research_system.name)

        if del_key and req_status not in filter_by_delegate_status:
            # get the delegate from question_response
            q = Question.objects.get(key=del_key)
            rq_qs = RequestQuestionResponse.objects.filter(
                question=q, request=crams_request)
            if not rq_qs.exists():
                continue
            for rq in rq_qs.all():
                response = lang_utils.strip_lower(rq.question_response)
                if response in valid_delegate_names:
                    crams_project = crams_request.project
                    populate_projects_dict(
                        projects_dict, crams_project, crams_request)
        else:
            crams_project = crams_request.project
            populate_projects_dict(projects_dict, crams_project, crams_request)

    return projects_dict


def fetch_current_requests_for_status(req_status, e_research_systems):
    def fetch_active_requests_for_given_parent_qs(parent_qs):
        prov_filter = Q(request_status__code__in=db.REQUEST_STATUS_PROVISIONED)
        valid_qs = parent_qs.filter(prov_filter).values_list('id', flat=True)
        valid_ids = list(valid_qs)

        parent_list = parent_qs.exclude(prov_filter)
        parent_filter = prov_filter & Q(current_request__in=parent_list)
        qs = Request.objects.filter(
            parent_filter).order_by('-id', 'current_request')
        prev_parent = None
        for req in qs:
            if req.current_request == prev_parent:
                continue
            valid_ids.append(req.id)
            prev_parent = req.current_request
        return Request.objects.filter(id__in=valid_ids)

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    ret_qs = Request.objects.none()
    base_qs = Request.objects.filter(
        e_research_system__name__in=e_research_systems,
        current_request__isnull=True)

    include_status_codes = None
    exclude_status_codes = None
    extra_qs = None
    if req_status.lower() == api.REQ_EXPIRY:
        base_qs = base_qs.filter(end_date__lt=current_date)
        exclude_status_codes = [db.REQUEST_STATUS_NEW,
                                db.REQUEST_STATUS_SUBMITTED,
                                db.REQUEST_STATUS_DECLINED]
    else:
        base_qs = base_qs.filter(end_date__gte=current_date)
        if req_status.lower() == api.REQ_ACTIVE:
            extra_qs = fetch_active_requests_for_given_parent_qs(base_qs)
        else:
            if req_status.lower() == api.REQ_NEW:
                include_status_codes = [db.REQUEST_STATUS_SUBMITTED,
                                        db.REQUEST_STATUS_UPDATE_OR_EXTEND]
            elif req_status.lower() == api.REQ_APPROVED:
                include_status_codes = [db.REQUEST_STATUS_APPROVED]

    if include_status_codes:
        ret_qs = base_qs.filter(
            request_status__code__in=include_status_codes)
    if exclude_status_codes:
        ret_qs = base_qs.exclude(
            request_status__code__in=exclude_status_codes)

    if extra_qs:
        ret_qs |= extra_qs

    ret_qs = ret_qs.select_related(
            'project', 'e_research_system__e_research_body',
            'funding_scheme__funding_body', 'request_status',
            'created_by', 'updated_by', 'current_request').prefetch_related(
            'project__created_by',
            'project__updated_by',
            'project__project_question_responses__question',
            'project__project_contacts__contact__organisation',
            'project__project_contacts__contact__contact_details',
            'project__project_contacts__contact_role',
            'project__linked_provisiondetails__provision_details',
            'storage_requests__provision_id',
            'storage_requests__storage_product__provider',
            'storage_requests__provision_details',
            'storage_requests__storage_question_responses__question',
            'compute_requests__compute_product',
            'compute_requests__provision_details',
            'compute_requests__compute_request_responses__question',
            'history',
        )

    return ret_qs.order_by('project__title')


def populate_projects_dict(projects_dict, crams_project, crams_request):
    """
        populate_projects_dict
    :param projects_dict:
    :param crams_project:
    :param crams_request:
    """
    proj_id = crams_project.id
    found_project = projects_dict.get(proj_id)
    # if a project contains many request, we have to append all requests in it
    if found_project is None:
        projects_dict[proj_id] = {
            'project': crams_project, 'requests': [crams_request]}
    else:
        found_project['requests'].append(crams_request)


def populate_project_list_response(
        rest_request, projects_dict, include_request_flag):
    ret_dict = {}
    user_obj = rest_request.user
    crams_token_dict = ContactErbRoleSerializer.fetch_cramstoken_roles_dict(user_obj)
    ret_dict['user'] = UserSerializer(user_obj).data

    project_list = []
    ret_dict['projects'] = project_list

    pd_context = AllocationProvisionDetailsSerializer.build_context_obj(user_obj)

    for key in projects_dict.keys():

        proj_dict = projects_dict.get(key)
        proj = proj_dict['project']
        reqs = proj_dict['requests']

        pd_list = []
        for ppd in proj.linked_provisiondetails.all():
            pd_serializer = AllocationProvisionDetailsSerializer(ppd.provision_details, context=pd_context)
            pd_list.append(pd_serializer.data)

        project_dict = {}
        project_list.append(project_dict)
        project_dict['title'] = proj.title
        project_dict['id'] = proj.id
        project_dict['crams_id'] = proj.crams_id

        project_dict['updated_by'] = \
            BaseRequestUtils.get_restricted_updated_by(
                reqs[0], crams_token_dict)

        if include_request_flag:
            request_list = []
            project_dict['requests'] = request_list
            for crams_req in reqs:
                request_list.append(populate_request_data(
                    crams_req, user_obj, crams_token_dict))

    return Response(ret_dict)


def populate_request_data(crams_request, user_obj, crams_token_dict):
    """
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

    fn = BaseRequestUtils.get_restricted_updated_by
    request_dict['updated_by'] = fn(crams_request, crams_token_dict)

    compute_list = []
    request_dict['compute_requests'] = compute_list
    pd_context = AllocationProvisionDetailsSerializer.build_context_obj(
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
    pd_context = AllocationProvisionDetailsSerializer.build_context_obj(
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
