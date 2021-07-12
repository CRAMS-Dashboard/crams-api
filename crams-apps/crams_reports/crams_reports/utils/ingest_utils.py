# coding=utf-8
"""

"""
from django.db.models import Q, Prefetch

from crams.utils import date_utils
from crams.models import EResearchBody, EResearchBodySystem
from crams_allocation.models import Request
from crams_allocation.constants import db
from crams_storage.models import StorageProduct, StorageProductProvisionId
from crams_collection.models import Project
from crams_allocation.product_allocation.models import StorageRequest
from crams_resource_usage.storage.models import StorageUsageIngest


def get_crams_transaction_id_map():
    CRAMS_ERB = EResearchBody.objects.get(name__iexact='crams')
    CRAMS_ERBS = EResearchBodySystem.objects.get(name__iexact='crams', e_research_body=CRAMS_ERB)
    ret_dict = dict()
    for r in Request.objects.filter(
            e_research_system=CRAMS_ERBS,
            request_status__code=db.REQUEST_STATUS_PROVISIONED):
        pid_qs = r.project.project_ids.filter(system__e_research_body=CRAMS_ERB)
        if pid_qs.exists():
            ret_dict[r.transaction_id] = pid_qs.first()
        else:
            ret_dict[r.transaction_id] = r.project.project_ids.first()
    return ret_dict


def get_crams_product_dict():
    CRAMS_ERB = EResearchBody.objects.get(name__iexact='crams')
    CRAMS_ERBS = EResearchBodySystem.objects.get(name__iexact='crams', e_research_body=CRAMS_ERB)
    ret_dict = dict()

    for sp in StorageProduct.objects.filter(e_research_system=CRAMS_ERBS):
        ret_dict[sp.name] = sp

    if 'Market-File' in ret_dict:
        ret_dict['Market.Monash.File'] = ret_dict['Market-File']
    return ret_dict


def get_storage_product_provision_id_dict(storage_product_object):
    ret_dict = dict()
    provision_id_qs = StorageProductProvisionId.objects.filter(
        storage_product=storage_product_object)

    for provision_id_obj in provision_id_qs:
        ret_dict[provision_id_obj.provision_id] = provision_id_obj
    return ret_dict


def get_provision_id_obj_fn_for_sp(storage_product_obj):
    def return_fn(search_provision_id):
        return p_dict.get(search_provision_id)

    p_dict = get_storage_product_provision_id_dict(storage_product_obj)
    return return_fn


def get_current_project_list(project_qs):
    current_projects = set()
    for p in project_qs.all():
        current_project = p.current_project or p
        current_projects.add(current_project)
    return current_projects


def sum_project_product_latest_allocated_gb(
        project_qs, storage_product_qs=None, override_null_project_qs=True):

    sp_allocated_dict = dict()
    sp_qs = storage_product_qs or StorageProduct.objects.all()
    for sp in sp_qs.all():
        sp_allocated_dict[sp] = float(0)

    if override_null_project_qs:
        if not project_qs or not project_qs.exists():
            project_qs = Project.objects.all()
    elif not project_qs or not project_qs.exists():
        return sp_allocated_dict

    current_projects = get_current_project_list(project_qs)

    qs_filter = Q(request__project__in=current_projects,
                  request__current_request__isnull=True)
    if storage_product_qs:
        qs_filter &= Q(storage_product__in=storage_product_qs)

    sr_qs = StorageRequest.objects.filter(qs_filter).select_related('storage_product')
    for sr in sr_qs:
        sp = sr.storage_product
        allocated_gb = sp_allocated_dict.get(sp) + sr.current_quota
        # if storage product has been provisioned use the approved quota
        if sr.provision_details:
            if sr.provision_details.status == 'P':
                allocated_gb = sp_allocated_dict.get(sp) + sr.approved_quota_total   
        sp_allocated_dict[sp] = allocated_gb
    return sp_allocated_dict


def get_storage_requests(request_status_code, project_qs,
                         storage_product_filter=None,
                         max_extract_date=date_utils.get_current_date()):
    project_filter = Q(request__project__in=project_qs)
    project_filter |= Q(request__project__current_project__in=project_qs)
    f_status = Q(request__request_status__code=request_status_code)
    project_sr_qs = StorageRequest.objects.filter(
        project_filter, f_status)
    if storage_product_filter:
        project_sr_qs = \
            project_sr_qs.filter(storage_product__in=storage_product_filter)

    ingest_extract_date_qs = \
        StorageUsageIngest.objects.filter(
            extract_date__lte=max_extract_date)
    spp_model = StorageProductProvisionId
    provision_id_qs = spp_model.objects.select_related(
        'storage_product').prefetch_related(
        Prefetch('ingests', queryset=ingest_extract_date_qs))

    return project_sr_qs.exclude(provision_id__isnull=True).select_related(
        'provision_id__storage_product', 'request__request_status',
        'storage_product__provider',
        'request__e_research_system__e_research_body').prefetch_related(
        Prefetch('provision_id', queryset=provision_id_qs))


def get_provisioned_storage_requests(project_qs, storage_product_qs):
    return get_storage_requests(db.REQUEST_STATUS_PROVISIONED, project_qs, storage_product_qs)


def get_provision_id_latest_sui_dict(storage_request_prefetch_qs):
    provision_id_sui_dict = dict()
    product_set = set()

    for sr in storage_request_prefetch_qs.order_by('-id'):
        if not sr.provision_id:
            continue
        if sr.provision_id in provision_id_sui_dict:
            continue
        if sr.request.current_request and \
                sr.storage_product in product_set:
            # historical provision id for a product already calculated, cannot use another.
            continue

        product_set.add(sr.storage_product)
        history_exists = False
        latest_sui = None
        for sui in sr.provision_id.ingests.all().order_by('-extract_date'):
            if not latest_sui:
                latest_sui = sui
            elif not history_exists:
                history_exists = True
                break
        provision_id_sui_dict[sr.provision_id] = latest_sui, sr, history_exists
    return provision_id_sui_dict
