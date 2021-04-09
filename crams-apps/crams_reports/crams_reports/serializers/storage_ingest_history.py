# coding=utf-8
"""

"""
import collections

from crams_allocation.config.allocation_config import STORAGE_PRODUCT_ALLOC_NEG
from crams_allocation.product_allocation.models import StorageRequest
from crams_resource_usage.storage.models import StorageUsageIngest
from crams_storage.models import StorageProductProvisionId
from rest_framework import serializers

from crams_reports.serializers.base import BaseReportSerializer


class StorageProductProvisionIDSerializer(BaseReportSerializer):
    provision_id = serializers.SerializerMethodField()
    readable_provision_id = serializers.SerializerMethodField()
    project_title = serializers.SerializerMethodField()
    storage_product_id = serializers.SerializerMethodField()
    storage_product = serializers.SerializerMethodField()

    ingested_usage = serializers.SerializerMethodField()

    class Meta(object):
        model = StorageProductProvisionId
        read_only = True
        fields = ('provision_id', 'readable_provision_id', 'project_title',
                  'storage_product_id', 'storage_product', 'ingested_usage')

    @classmethod
    def get_provision_id(cls, obj):
        return obj.id

    @classmethod
    def get_readable_provision_id(cls, obj):
        return obj.provision_id

    @classmethod
    def get_project_title(cls, obj):
        storage_requests = \
            StorageRequest.objects.filter(provision_id=obj)
        if storage_requests:
            current_qs = storage_requests.filter(
                request__current_request__isnull=True)
            if current_qs.exists():
                storage_requests = current_qs
            return storage_requests.order_by('-id')[0].request.project.title
        else:
            return None

    @classmethod
    def get_storage_product_id(cls, obj):
        storage_requests = \
            StorageRequest.objects.filter(provision_id=obj)
        if storage_requests:
            return storage_requests[0].storage_product_id
        else:
            return None

    @classmethod
    def get_storage_product(cls, obj):
        storage_requests = \
            StorageRequest.objects.filter(provision_id=obj)
        if storage_requests:
            return storage_requests[0].storage_product.name
        else:
            return None

    @classmethod
    def does_negative_mean_unlimited(cls, storage_product):
        if storage_product.name in STORAGE_PRODUCT_ALLOC_NEG:
            return True
        else:
            return False

    @classmethod
    def get_ingested_usage(cls, obj):
        results = []
        usage_ingest = StorageUsageIngest.objects.filter(
            provision_id=obj).prefetch_related('provision_id__storage_product')

        for item in usage_ingest:
            ordered_dict = collections.OrderedDict()

            ordered_dict['extract_date'] = item.extract_date
            ordered_dict['allocated_gb'] = item.reported_allocated_gb

            # get the total used gb
            used_gb = item.ingested_gb_tape + item.ingested_gb_disk
            ordered_dict['used_gb'] = \
                float('{0:.2f}'.format(round(used_gb), 2))

            ordered_dict['used_disk'] = item.ingested_gb_disk
            ordered_dict['used_tape'] = item.ingested_gb_tape

            # get the storage product unit cost
            unit_cost = item.provision_id.storage_product.unit_cost
            ordered_dict['allocated_cost'] = \
                float('{0:.2f}'.format(round(unit_cost * (
                    item.reported_allocated_gb/1000), 2)))
            ordered_dict['used_cost'] = \
                float('{0:.2f}'.format(round(unit_cost * (used_gb/1000), 2)))

            if item.reported_allocated_gb < 0:
                if cls.does_negative_mean_unlimited(obj.storage_product):
                    ordered_dict['allocated_gb'] = None
                    ordered_dict['allocated_cost'] = None

            results.append(ordered_dict)

        return results
