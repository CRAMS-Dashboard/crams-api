# coding=utf-8
"""

"""

from crams.utils.lang_utils import strip_lower

from crams_collection.utils import project_user_utils
from crams_allocation.config import allocation_config
from crams_allocation.constants import db_qs
from crams.constants import db
from crams_allocation.models import Request
from crams.models import EResearchBody
from crams.models import ProvisionDetails


def get_product_e_system_name(product_obj):
    """
    ==> from d3_prod crams.common.utils.request_utils
    """
    if product_obj.e_research_system:
        return product_obj.e_research_system.name
    elif product_obj.funding_body:
        return product_obj.funding_body.name
    return None


def get_erb_request_status_dict(crams_request_obj):
    request_status = crams_request_obj.request_status
    request_erbs_obj = crams_request_obj.e_research_system

    ret_dict = {
        # 'id': request_status.id,
        "code": request_status.code,
        "status": request_status.status,
        "display_name": request_status.status
    }
    display_qs = db_qs.ERB_REQUEST_STATUS_QS.filter(
        request_status=crams_request_obj.request_status,
        extension_count_data_point__lte=crams_request_obj.allocation_extension_count)

    if display_qs.exists():
        erbs_display_qs = display_qs.filter(e_research_system=request_erbs_obj)
        if erbs_display_qs.exists():
            display_qs = erbs_display_qs
        else:
            erb_display_qs = display_qs.filter(e_research_body=request_erbs_obj.e_research_body)
            if erb_display_qs.exists():
                display_qs = erb_display_qs
        ret_dict['display_name'] = display_qs.order_by('extension_count_data_point')[0].display_name
    return ret_dict


class BaseRequestUtils:
    @classmethod
    def get_restricted_updated_by(cls, request, crams_token_dict):
        updated_by = None
        erb_name = request.e_research_system.e_research_body.name
        if request.request_status.code in allocation_config.RESTRICTED_ADMIN_STATUS:
            role_group_dict = allocation_config.UPDATED_BY_VISIBLE_ROLEGRP_FOR_ERB_LOWER
            for role_group in role_group_dict.get(
                    strip_lower(erb_name), list()):
                if role_group in crams_token_dict:
                    updated_by = request.updated_by
                    break
        else:
            updated_by = request.updated_by

        hide_user_val = erb_name
        if allocation_config.DEFAULT_UPDATED_BY_PREFIX:
            hide_user_val += ' ' + allocation_config.DEFAULT_UPDATED_BY_PREFIX
        return project_user_utils.user_details_json(updated_by, hide_user_val)


def get_e_system_or_fb(request_obj):
    if request_obj.e_research_system:
        return request_obj.e_research_system
    elif request_obj.funding_scheme:
        return request_obj.funding_scheme.funding_body
    return None


def get_e_system_name(request_obj):
    obj = get_e_system_or_fb(request_obj)
    if obj:
        return obj.name
    return None


def get_request_approver_email(request_obj):
    if not request_obj.request_status.code == db.REQUEST_STATUS_APPROVED:
        latest_request = request_obj.current_request or request_obj
        qs = Request.objects.filter(
            current_request=latest_request,
            request_status__code=db.REQUEST_STATUS_APPROVED).order_by('-id')
        if qs.exists():
            request_obj = qs.first()
    return request_obj.updated_by.email


def get_allocation_approve_provision_objects(
        project_qs_filter=None, request_id=None, e_research_body=None):
    def add_to_list(request_obj, p_list, in_approved_list):
        if request_obj.request_status.code == db.REQUEST_STATUS_PROVISIONED:
            p_list.append(request_obj)
        elif request_obj.request_status.code == db.REQUEST_STATUS_APPROVED:
            in_approved_list.append(request_obj)

    def sort_by_id(req_list):
        req_list.sort(key=lambda x: x.id)

    def map_nearest(obj, related_request_list):
        prev = None
        for admin_req in related_request_list:
            if obj.id >= admin_req.id:
                prev = admin_req.id
        return prev

    ret_dict = dict()
    request_qs = Request.objects.filter(current_request__isnull=True)
    if request_id:
        request_qs = request_qs.filter(pk=request_id)
    if project_qs_filter:
        request_qs = request_qs.filter(project__in=project_qs_filter)
    if e_research_body:
        if type(e_research_body) == str:
            e_research_body = EResearchBody.objects.get(
                name__iexact=e_research_body)
        elif type(e_research_body) == int:
            e_research_body = EResearchBody.objects.get(
                pk=e_research_body)
        else:
            return ret_dict
        request_qs.filter(e_research_system__e_research_body=e_research_body)

    for current_request in request_qs.prefetch_related('history__request_status').select_related('request_status'):
        alloc_list = [current_request] + list(current_request.history.all())

        provisioned_list = list()
        approved_list = list()
        for request in alloc_list:
            add_to_list(request, provisioned_list, approved_list)

        sort_by_id(provisioned_list)
        sort_by_id(approved_list)
        for request in alloc_list:
            ret_dict[request] = (map_nearest(request, provisioned_list),
                                 (map_nearest(request, approved_list)))
    return ret_dict


"""
from crams.common.utils import request_utils
id = 2085
tp_dict = request_utils.get_allocation_approve_provision_objects(id)

count = 10
for k, v in tp_dict.items():
    count = count - 1
    if count < 0:
        break
    print(k, v[0], v[1])
"""


def get_partial_provision_flag(request_obj):
    def get_partially_provisioned_flag(prod_request_qs):
        count_provisioned = 0
        status_required = ProvisionDetails.PROVISIONED
        for obj in prod_request_qs:
            if obj.provision_details:
                if obj.provision_details.status == status_required:
                    count_provisioned += 1
        if prod_request_qs and len(prod_request_qs) > 1:
            if count_provisioned > 0:
                return len(prod_request_qs) > count_provisioned
        return False

    fn = get_partially_provisioned_flag
    return {
        'compute_request': fn(request_obj.compute_requests.all()),
        'storage_request': fn(request_obj.storage_requests.all())
    }
