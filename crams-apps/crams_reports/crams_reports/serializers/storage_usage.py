# coding=utf-8
"""

"""


import collections

from crams.serializers.model_serializers import ReadOnlyModelSerializer
from crams_resource_usage.storage.models import StorageUsageIngest
from crams_collection.models import Project
from crams_reports.constants import report_constants
from crams_storage.models import StorageProduct
from rest_framework import serializers, exceptions

from crams_reports.utils import ingest_utils, product_utils


class BaseReportSerializer(ReadOnlyModelSerializer):
    USER_ERB_SYSTEMS_CONTEXT_KEY = 'user_erb_system_list'
    CONTACT_CONTEXT_KEY = 'contact'

    def __delete__(self, instance):
        raise exceptions.APIException('Delete not Allowed')

    def create(self, validated_data):
        raise exceptions.APIException('Create not allowed')

    def update(self, instance, validated_data):
        raise exceptions.APIException('Update not allowed')


class StorageProductIngestInfo:
    def __init__(self, size_gb, cost_per_tb):
        self.size_gb = size_gb
        self.size_tb = self.size_gb * report_constants.GB_TO_TB_METRIC_FACTOR
        self.cost = self.size_tb * cost_per_tb

    def to_dict(self):
        return {
            'size_gb': self.size_gb,
            'size_tb': self.size_tb,
            'cost': self.cost
        }

    def to_dict_display(self):
        return {
            'size_gb': "{0:.3f}".format(self.size_gb),
            'size_tb': "{0:.3f}".format(self.size_tb),
            'cost': "{0:.2f}".format(self.cost)
        }


class SPUIstore:
    def __init__(self, storage_ingest):
        # self.allocated_gb = delete_calc_total_allocated_gb(
        #     storage_ingest.project,
        #     storage_ingest.storage_product)
        self.allocated_gb = storage_ingest.allocated_gb

        self.available_gb = \
            self.allocated_gb - storage_ingest.total_ingested_gb
        self.overdraft_gb = 0
        if self.available_gb < 0:
            self.overdraft_gb = -1 * self.available_gb
            self.available_gb = 0

        self.unit_cost = \
            storage_ingest.storage_product.unit_cost
        self.used_disk = storage_ingest.ingested_gb_disk
        self.used_tape = storage_ingest.ingested_gb_tape


class StorageProductUsageReportSerializer(BaseReportSerializer):
    project = serializers.SerializerMethodField()

    storage_product = serializers.SerializerMethodField()

    allocated = serializers.SerializerMethodField()

    available = serializers.SerializerMethodField()

    overdraft = serializers.SerializerMethodField()

    ingested_disk = serializers.SerializerMethodField(method_name='get_disk')

    ingested_tape = serializers.SerializerMethodField(method_name='get_tape')

    class Meta(object):
        model = StorageUsageIngest
        fields = ('project', 'storage_product', 'allocated', 'available',
                  'overdraft', 'ingested_disk', 'ingested_tape',
                  'extract_date', 'reported_allocated_gb')

    @classmethod
    def get_project(cls, storage_ingest):
        return storage_ingest.project.title

    @classmethod
    def get_storage_product(cls, storage_ingest):
        return storage_ingest.storage_product.name

    def get_allocated(self, storage_ingest):
        calc = SPUIstore(storage_ingest)
        return StorageProductIngestInfo(
            calc.allocated_gb, calc.unit_cost).to_dict_display()

    def get_available(self, storage_ingest):
        calc = SPUIstore(storage_ingest)
        return StorageProductIngestInfo(
            calc.available_gb, calc.unit_cost).to_dict_display()

    def get_overdraft(self, storage_ingest):
        calc = SPUIstore(storage_ingest)
        return StorageProductIngestInfo(
            calc.overdraft_gb, calc.unit_cost).to_dict_display()

    def get_disk(self, storage_ingest):
        calc = SPUIstore(storage_ingest)
        return StorageProductIngestInfo(
            calc.used_disk, calc.unit_cost).to_dict_display()

    def get_tape(self, storage_ingest):
        calc = SPUIstore(storage_ingest)
        return StorageProductIngestInfo(
            calc.used_tape, calc.unit_cost).to_dict_display()


class ConsolidatedSUI:
    def __init__(self, storage_product, crams_total_allocated_gb):
        self.crams_allocated_gb = crams_total_allocated_gb
        self.storage_product = storage_product
        self.sui_present_allocated_gb_total = float(0)
        self.ingested_gb_disk = float(0)
        self.ingested_gb_tape = float(0)
        self.total_ingested_gb = float(0)
        self.sui_reported_allocated_gb = float(0)
        self.sui_sr_tuple_list = list()
        self.provision_id_set = set()
        self.consolidated_history_exists = False
        self.consolidated_sp_request_dict = dict()

    def add(self, sui, sr, history_exists):
        sp = sr.storage_product
        provision_sp = sui.provision_id.storage_product
        if sp == provision_sp and sp == self.storage_product:
            self.sui_present_allocated_gb_total += sr.approved_quota_total
            self.ingested_gb_disk += sui.ingested_gb_disk
            self.ingested_gb_tape += sui.ingested_gb_tape
            self.total_ingested_gb += sui.total_ingested_gb
            self.sui_reported_allocated_gb += sui.reported_allocated_gb
            self.sui_sr_tuple_list.append((sui, sr, history_exists))
            self.consolidated_history_exists |= history_exists

    def get_first_provision_dict(self):
        pk = None
        provision_id = None
        if self.sui_sr_tuple_list:
            print('processing sui .....', self.sui_sr_tuple_list)
            sui, sr, history_exists = self.sui_sr_tuple_list[0]
            if sui:
                pk = sui.provision_id.id
                provision_id = sui.provision_id.provision_id
        print('returning pid', pk, provision_id)
        return {
            'id': pk,
            'provision_id': provision_id
        }

    def ingests_missing_boolean(self):
        return self.crams_allocated_gb == self.sui_present_allocated_gb_total


class AbstractSPUsageSerializer(BaseReportSerializer):
    @classmethod
    def update_overdraft(cls, allocated, usage_dict):
        if not usage_dict:
            return
        used = usage_dict.get('Used (Disk)')
        tape = usage_dict.get('HSM (Tape)')
        overdraft = used + tape - allocated
        if overdraft < 0:
            available = -1 * overdraft
            overdraft = 0
        else:
            available = 0

        usage_dict['Over Draft'] = overdraft
        usage_dict['Available'] = available

    def fetch_required_storage_product_qs(self):
        e_research_system = self.fetch_e_research_system_param()
        if e_research_system:
            storage_product_qs = StorageProduct.objects.filter(
                e_research_system__name__iexact=e_research_system.lower()).\
                order_by('-name')
        else:
            storage_product_qs = \
                StorageProduct.objects.all().order_by(
                    'e_research_system', '-name')
        return storage_product_qs

    @classmethod
    def build_product_summary(cls, sp_list, summary_dict):
        summary_required_group = \
            ['usage', 'cost', 'total', 'cost_cap', 'cost_op']
        for sp_dict in sp_list:
            for group_key, group_dict in sp_dict.items():
                if group_key in summary_required_group:
                    if group_key not in summary_dict:
                        summary_dict[group_key] = collections.OrderedDict()
                    curr_dict = summary_dict.get(group_key)
                    for col_key, value in group_dict.items():
                        if col_key not in curr_dict:
                            curr_dict[col_key] = 0.0
                        curr_dict[col_key] += value

        tdict = summary_dict.get('total')
        used_percent = 0
        t_allocated = tdict['allocated_gb_size']
        if t_allocated:
            used_percent = tdict['used_gb_size'] / t_allocated
        tdict['used_percent'] = used_percent * 100

        cls.update_overdraft(t_allocated, summary_dict.get('usage'))
        cls.update_overdraft(
            tdict['allocated_cost'], summary_dict.get('cost'))
        cls.update_overdraft(
            tdict['allocated_cost_cap'], summary_dict.get('cost_cap'))
        cls.update_overdraft(
            tdict['allocated_cost_op'], summary_dict.get('cost_op'))

        flags = {
            'alert_user': False,
            'raise_error': False,
            'history': False,
            'zero_allocation_usage': False
        }
        usage_dict = summary_dict.get('usage', None)
        if usage_dict:
            flags['alert_user'] = usage_dict.get('Over Draft', 0) > 0
        summary_dict['flags'] = flags

    def calculate_product_usage(self, project_qs):
        # start with empty summary dict
        summary_dict = collections.OrderedDict()

        # storage product provision ID
        summary_dict['provision'] = {
            'id': None,
            'provision_id': None
        }

        # storage product
        summary_dict['product'] = {
                'id': 0,
                'name': 'Aggregated Total'
            }

        sp_list = list()
        sp_list.append(summary_dict)
        alloc_calc_fn = ingest_utils.sum_project_product_latest_allocated_gb
        sp_allocated_dict = alloc_calc_fn(project_qs)
        storage_product_qs = self.fetch_required_storage_product_qs()
        storage_request_prefetch_qs = \
            ingest_utils.get_provisioned_storage_requests(
                project_qs, storage_product_qs)
        provision_id_sui_dict = ingest_utils.get_provision_id_latest_sui_dict(
            storage_request_prefetch_qs)

        sp_consolidated_dict = dict()
        for sp in storage_product_qs.all():
            sp_allocated_gb = sp_allocated_dict.get(sp, float(0))
            sp_consolidated_dict[sp] = ConsolidatedSUI(sp, sp_allocated_gb)

        for provision_id, (latest_sui, sr, history_exists) in \
                provision_id_sui_dict.items():
            sp = provision_id.storage_product
            consolidated_sui = sp_consolidated_dict.get(sp)
            if latest_sui:
                consolidated_sui.add(latest_sui, sr, history_exists)

        # return_allocated_only = self.fetch_allocated_only_param()

        for sp in storage_product_qs.all().order_by('-name'):
            consolidated_sui = sp_consolidated_dict.get(sp)

            product_dict = collections.OrderedDict()
            sp_list.append(product_dict)
            product_dict['product'] = {
                'id': sp.id,
                'name': sp.name
            }
            if not consolidated_sui:
                continue

            provision_dict = consolidated_sui.get_first_provision_dict()
            provision_id = provision_dict.get('provision_id')
            product_dict['provision'] = provision_dict

            flags = {
                'alert_user': False,
                'raise_error': False,
                'history': consolidated_sui.consolidated_history_exists,
                'zero_allocation_usage': False,
                'ingests_missing': consolidated_sui.ingests_missing_boolean()
            }
            product_dict['flags'] = flags

            total = collections.OrderedDict()
            product_dict['total'] = total

            allocated_gb = consolidated_sui.crams_allocated_gb
            total['allocated_gb_size'] = allocated_gb

            cap_cost, op_cost, total_cost = product_utils.calc_product_cost(sp, allocated_gb)
            total['allocated_cost'] = total_cost
            total['allocated_cost_cap'] = cap_cost
            total['allocated_cost_op'] = op_cost

            used_gb = used_disk = used_tape = 0
            if consolidated_sui:
                used_gb = consolidated_sui.total_ingested_gb
                used_disk = consolidated_sui.ingested_gb_disk
                used_tape = consolidated_sui.ingested_gb_tape
            total['used_gb_size'] = used_gb

            cap_cost, op_cost, total_cost = product_utils.calc_product_cost(sp, used_gb)
            total['used_cost'] = total_cost
            total['used_cost_cap'] = cap_cost
            total['used_cost_op'] = op_cost

            if allocated_gb <= 0:
                if used_gb > 0:
                    # prevent error if allocation has provision id and history
                    if not provision_id and not flags['history']:
                        flags['raise_error'] = True

            used_percent = float(0)
            if allocated_gb:
                used_percent = (used_gb * 100.0) / allocated_gb
            elif flags['raise_error']:
                flags['zero_allocation_usage'] = True
                reported_alloc_gb = consolidated_sui.sui_reported_allocated_gb
                used_percent = (used_gb * 100.0) / reported_alloc_gb

            if used_percent >= report_constants.ALERT_USAGE_PERCENT:
                flags['alert_user'] = True
            total['used_percent'] = used_percent

            usage = collections.OrderedDict()
            product_dict['usage'] = usage
            available_gb = allocated_gb - used_gb
            usage['Available'] = available_gb
            usage['Used (Disk)'] = used_disk
            usage['HSM (Tape)'] = used_tape
            if available_gb < 0:
                usage['Over Draft'] = available_gb * -1
                usage['Available'] = 0
            else:
                usage['Over Draft'] = 0

            cost = collections.OrderedDict()
            product_dict['cost'] = cost
            cap = collections.OrderedDict()
            product_dict['cost_cap'] = cap
            op = collections.OrderedDict()
            product_dict['cost_op'] = op
            cap['Available'], op['Available'], cost['Available'] = \
                product_utils.calc_product_cost(sp, usage['Available'])
            cap['Used (Disk)'], op['Used (Disk)'], cost['Used (Disk)'] = \
                product_utils.calc_product_cost(sp, usage['Used (Disk)'])
            cap['HSM (Tape)'], op['HSM (Tape)'], cost['HSM (Tape)'] = \
                product_utils.calc_product_cost(sp, usage['HSM (Tape)'])
            cap['Over Draft'], op['Over Draft'], cost['Over Draft'] = \
                product_utils.calc_product_cost(sp, usage['Over Draft'])

        self.build_product_summary(sp_list, summary_dict)

        return sp_list

    def fetch_e_research_system_param(self):
        e_research_system = None
        if self.context:
            context_request = self.context['request']
            e_research_system = context_request.query_params.get(
                report_constants.EResearch_System_NAME_PARAM, None)
            if not e_research_system:
                e_research_system = context_request.query_params.get(
                    report_constants.FB_NAME_PARAM, None)
        return e_research_system

    def fetch_allocated_only_param(self):
        if self.context:
            param = report_constants.RETURN_ALLOCATED_ONLY_PARAM
            if self.context['request'].query_params.get(param, None):
                return True
        return False


class ProjectSPUsageSerializer(AbstractSPUsageSerializer):
    project = serializers.SerializerMethodField()
    storage_product = serializers.SerializerMethodField()

    class Meta(object):
        model = Project
        fields = ('project', 'storage_product')

    def get_project(self, project_obj):
        request_qs = project_obj.requests.all()
        e_research_system = self.fetch_e_research_system_param()

        if e_research_system:
            request_qs = project_obj.requests.filter(
                e_research_system__name__iexact=e_research_system.lower())
        return {
            'id': project_obj.id,
            'title': project_obj.title,
            'requests': [req.id for req in request_qs]
        }

    def get_storage_product(self, project_obj):
        project_qs = Project.objects.filter(pk=project_obj.id)
        val = self.calculate_product_usage(project_qs)
        return val
