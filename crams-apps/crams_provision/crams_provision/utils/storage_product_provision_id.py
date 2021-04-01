# coding=utf-8
"""

"""
import datetime
import pytz

from django.db import models

from crams_allocation.constants import db as allocation_db_constants


class StorageProductProvisionIdUtils:
    @classmethod
    def current_storage_request_for_storageproduct_provision_id(cls, spp_obj):
        s_request = spp_obj.storage_requests.filter(request__current_request__isnull=True)
        count = s_request.count()
        if count > 1:
            msg = 'ProvisionId {} related to multiple projects, pk={}'
            raise Exception(msg.format(spp_obj.provision_id, spp_obj.id))
        elif count == 0:
            s_request = spp_obj.storage_requests.all()
            if not s_request.exists():
                msg = 'ProvisionId {} not related to request'
                raise Exception(msg.format(spp_obj.provision_id))

        return s_request.latest('id')

    @classmethod
    def last_provisioned_storage_request_for_storage_provision_id(
            cls, spp_obj, max_date=None, enforce_max_date=False):
        provision_status = [allocation_db_constants.REQUEST_STATUS_PROVISIONED,
                            allocation_db_constants.REQUEST_STATUS_PARTIAL_PROVISIONED]
        request_status_filter = models.Q(
            request__request_status__code__in=provision_status,
            storage_product=spp_obj.storage_product)
        qs = spp_obj.storage_requests.filter(request_status_filter)
        if max_date:
            ts = datetime.datetime(max_date.year, max_date.month, max_date.day)
            ts = ts.replace(tzinfo=pytz.UTC)
            qs_max_date = qs.filter(request__creation_ts__lte=ts)
            if qs_max_date.exists() or enforce_max_date:
                qs = qs_max_date
            else:
                print('no max date sr', max_date, spp_obj)

        if qs.exists():
            return qs.order_by('-id').first()
        return None

    @classmethod
    def current_request_for_storageproduct_provision_id(cls, spp_obj):
        return cls.current_storage_request_for_storageproduct_provision_id(spp_obj=spp_obj).request

    @classmethod
    def get_allocated_gb(cls, spp_obj, date_ts_required=None):
        qs = spp_obj.storage_requests.filter(
            request__request_status__code=allocation_db_constants.REQUEST_STATUS_PROVISIONED)
        if date_ts_required:
            qs = qs.filter(request__creation_ts__lte=date_ts_required)
        if qs.count() == 0:
            return 0
        sr = qs.latest('id')
        return sr.approved_quota_total
