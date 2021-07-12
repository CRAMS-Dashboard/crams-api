# coding=utf-8
"""RequestSerializers."""

import copy
import logging

from crams.constants import db
from crams.models import FundingScheme
from crams.models import Question
from crams.serializers import lookup_serializers
from crams.serializers import utilitySerializers as utility_serializers
from crams_compute.models import ComputeProduct
from crams_log import log_process
from crams_log.utils import validation_utils as log_validation_utils
from crams_storage.serializers.storage_product_serializers import StorageProductZoneOnlySerializer
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.exceptions import ValidationError

from crams_allocation.config import allocation_config
from crams_allocation.config import transaction_id as transaction_id_config
from crams_allocation.config.allocation_config import CRAMS_REQUEST_PARENT
from crams_allocation.log.allocation_request_log import RequestMetaLogger
from crams_allocation.models import Request, AllocationHome
from crams_allocation.models import RequestStatus, NotificationTemplate
from crams_allocation.product_allocation.models import StorageRequest
from crams_allocation.product_allocation.serializers.compute_request import ComputeRequestSerializer
from crams_allocation.product_allocation.serializers.storage_request_serializers import StorageRequestSerializer
from crams_allocation.serializers import question_serializers
from crams_allocation.serializers.base import ReadOnlyCramsRequestWithoutProjectSerializer
from crams_allocation.serializers.product_request import ProductRequestSerializer
from crams_allocation.utils import lookup_data
from datetime import datetime

User = get_user_model()
LOG = logging.getLogger(__name__)


class CramsRequestWithoutProjectSerializer(ReadOnlyCramsRequestWithoutProjectSerializer):
    """class CramsRequestSerializer."""

    compute_requests = serializers.SerializerMethodField()

    storage_requests = serializers.SerializerMethodField()

    # request question response
    request_question_responses = serializers.SerializerMethodField()

    request_status = serializers.SerializerMethodField()

    funding_scheme = utility_serializers.PrimaryKeyLookupField(
        many=False, required=False, allow_null=True,
        fields=['id', 'funding_scheme'], queryset=FundingScheme.objects.all())

    e_research_system = lookup_serializers.EResearchSystemSerializer(
        required=False, allow_null=True)

    funding_body = serializers.SerializerMethodField(method_name='get_fb_name')

    allocation_home = serializers.SlugRelatedField(
        many=False, slug_field='code', required=False, allow_null=True,
        queryset=AllocationHome.objects.all())

    updated_by = serializers.SerializerMethodField()

    historic = serializers.SerializerMethodField(method_name='is_historic')

    readonly = serializers.SerializerMethodField()

    class Meta(object):
        model = Request
        fields = ['id', 'start_date', 'end_date', 'approval_notes', 'historic',
                  'compute_requests', 'storage_requests', 'funding_scheme',
                  'funding_body', 'e_research_system', 'national_percent', 'allocation_home',
                  'transaction_id', 'readonly', 'request_status', 'data_sensitive',
                  'request_question_responses', 'updated_by', 'sent_email', 'creation_ts']

        read_only_fields = ['creation_ts', 'last_modified_ts', 'updated_by',
                            'request_status', 'funding_body', 'transaction_id']

    def validate_min_max_related_objects(self, data):
        def validate_min_max_anon(list_field_name):
            field_data_list = self.initial_data.get(list_field_name, [])
            min_val = min_max_dict.get(allocation_config.MINIMUM)
            if min_val and len(field_data_list) < min_val:
                err_msg = 'A minimum of {} {} is required for {}'. \
                    format(min_val, list_field_name, system_name)
                raise ValidationError(err_msg)
            max_val = min_max_dict.get(allocation_config.MAXIMUM)
            if max_val and len(field_data_list) > max_val:
                err_msg = 'A maximum of {} {} is allowed for {}'. \
                    format(max_val, list_field_name, system_name)
                raise ValidationError(err_msg)

        msg = 'either e_research_system or funding_scheme is required.'
        if 'funding_scheme' not in data and 'e_research_system' not in data:
            raise ValidationError({
                'e_research_system': msg
            })

        if 'start_date' not in data:
            raise ValidationError({
                'start_date': 'This field is required.'
            })

        if 'end_date' not in data:
            raise ValidationError({
                'end_date': 'This field is required.'
            })

        input_status_code_dict = data.get('request_status', None)
        if input_status_code_dict:
            raise ValidationError('Request Status: status is a \
                                  calculated value, cannot be set')

        e_research_system = data.get('e_research_system')
        if e_research_system:
            system_name = e_research_system.name
        else:
            funding_scheme = data.get('funding_scheme')
            system_name = funding_scheme.funding_body.name

        # Validate min/max for Storage Requests
        min_max_dict = allocation_config.REQUEST_STORAGE_PRODUCT_PER_SYSTEM.get(system_name)
        if min_max_dict:
            field_name = 'storage_requests'
            validate_min_max_anon(field_name)

    @classmethod
    def validate_e_research_system(cls, data):
        if data:
            return lookup_data.get_e_research_system_obj(data)

    @classmethod
    def validate_allocation_percentage(
            cls, crams_action_state, national_percent, allocation_home_obj):
        if crams_action_state.is_create_action:
            if national_percent or allocation_home_obj:
                raise ValidationError(
                    'allocation percent/node can only be set at approval time')
            return 100

        request_obj = crams_action_state.existing_instance
        if national_percent is None:
            if request_obj.request_status not in db.NEW_REQUEST_STATUS:
                raise ValidationError(
                    'request allocation percent is required')
        if national_percent == 100 and allocation_home_obj:
            raise ValidationError(
                'Allocation Node cannot be set if National Percent is 100')
        elif national_percent < 100 and not allocation_home_obj:
            raise ValidationError(
                'Allocation Node must be set if National Percent is not 100')

        if not crams_action_state.is_partial_action:
            if allocation_home_obj != request_obj.allocation_home or \
                    national_percent != request_obj.national_percent:
                raise ValidationError(
                    'allocation percent/node can only be set at approval time')

        return national_percent

    @classmethod
    def validate_funding_scheme(cls, funding_scheme_data):
        # Set funding scheme
        funding_scheme_obj = None
        if funding_scheme_data and 'id' in funding_scheme_data:
            funding_scheme_id = funding_scheme_data['id']
            try:
                funding_scheme_obj = FundingScheme.objects.get(
                    pk=funding_scheme_id)
            except FundingScheme.DoesNotExist:
                raise ParseError('Funding Scheme not found for id {}'
                                 .format(funding_scheme_id))
            except FundingScheme.MultipleObjectsReturned:
                raise ParseError('Multiple Funding Schemes found for id {}'
                                 .format(funding_scheme_id))
        return funding_scheme_obj

    def add_validate_related_compute_requests(self, input_compute_requests):
        def fetch_compute_product(cp_dict):
            if not cp_dict:
                raise ValidationError('Compute Product is required')
            pk = cp_dict.get('id')
            try:
                return ComputeProduct.objects.get(pk=pk)
            except ComputeProduct.DoesNotExist:
                err_msg = 'Compute Product not found for id = {}'
                raise ValidationError(err_msg.format(pk))

        def validate_compute_requests(cr_dict_list):
            ret_list = list()
            for cr in cr_dict_list:
                remove = cr.get('remove', False)
                if remove:  # this compute request is retired
                    continue
                parent = cr.pop('parent_cr', None)
                comp_sz = ComputeRequestSerializer(data=cr, context=self.context)
                comp_sz.is_valid(raise_exception=True)
                ret_list.append((parent, comp_sz))
            return ret_list

        crams_action_state = self.get_action_state()
        existing_request_obj = crams_action_state.existing_instance
        if not existing_request_obj:
            return validate_compute_requests(input_compute_requests)

        parent_cp_map = dict()
        for cr_obj in existing_request_obj.compute_requests.all():
            if cr_obj.compute_product in parent_cp_map:
                msg = 'in-consistent data, Product {} not unique in request {}'
                raise ValidationError(
                    msg.format(cr_obj.compute_product, existing_request_obj))
            parent_cp_map[cr_obj.compute_product] = cr_obj

        # ensure compute product is unique in current Request
        curr_cp_map = dict()
        for cr_dict in input_compute_requests:
            cp = fetch_compute_product(cr_dict.get('compute_product'))
            if curr_cp_map and cp in curr_cp_map:
                msg = '{} must be unique per Request'
                raise ValidationError(msg.format(cp))
            if parent_cp_map and cp in parent_cp_map:
                cr_dict['parent_cr'] = parent_cp_map.pop(cp)

        pd_context = ComputeRequestSerializer.show_error_msg_context()
        for cp, cr_remaining in parent_cp_map.items():
            new_cr = copy.copy(cr_remaining)
            new_cr.id = None
            sz = ComputeRequestSerializer(new_cr, context=pd_context)
            cr_dict = sz.data
            cr_dict['parent_cr'] = cr_remaining
            input_compute_requests.append(cr_dict)

        return validate_compute_requests(input_compute_requests)

    def add_validate_related_storage_requests(self, input_storage_requests):
        def fetch_storage_product(sp_dict):
            if not sp_dict:
                raise ValidationError('Storage Product is required')
            storage_sz = StorageProductZoneOnlySerializer(
                data=sp_dict)
            storage_sz.is_valid(raise_exception=False)
            if storage_sz.errors:
                err_list.append(storage_sz.errors)
            else:
                if storage_sz.instance:
                    return storage_sz.instance
            return lookup_data.get_storage_product_obj(storage_sz.data)

        def validate_approved_quota(sr_input_dict):
            if self.instance:
                if self.instance.request_status.code in db.REQUEST_STATUS_PROVISIONED:
                    approved_quota = sr_input_dict.get('approved_quota_change', None)
                    if approved_quota:
                        err_list.append('Approved quota cannot be set for Provisioned products')

        def validate_storage_requests(sr_dict_list):
            ret_list = list()
            for sr in sr_dict_list:
                validate_approved_quota(sr)
                existing_quota = sr.get('current_quota')
                parent = sr.pop('parent_sr', None)
                storage_sz = StorageRequestSerializer(data=sr, context=self.context)
                storage_sz.is_valid(raise_exception=False)
                if storage_sz.errors:
                    err_list.append(storage_sz.errors)
                else:
                    ret_list.append((parent, storage_sz, existing_quota))
            return ret_list

        crams_action_state = self.get_action_state()
        existing_request_obj = crams_action_state.existing_instance
        if not existing_request_obj:
            return validate_storage_requests(input_storage_requests)

        new_request_status_is_declined = False
        is_admin_action = crams_action_state.is_partial_action
        if crams_action_state.is_partial_action:
            if crams_action_state.override_data \
                    and 'request_status' in crams_action_state.override_data:
                new_rstatus = \
                    crams_action_state.override_data.get('request_status')
                if new_rstatus in db.DECLINED_STATES:
                    new_request_status_is_declined = True

        parent_sp_map = dict()
        err_list = list()
        for sr_obj in existing_request_obj.storage_requests.all():
            curr_status = existing_request_obj.request_status.code
            if sr_obj.approved_quota_total == 0 and sr_obj.approved_quota_change == 0:
                if curr_status == db.REQUEST_STATUS_PROVISIONED:
                    # Zeroed out storage product request is not propagated
                    continue
            # if curr_status not in db.DRAFT_STATES:
            #     if sr_obj.current_quota == 0 and sr_obj.requested_quota_change == 0:
            #         msg = 'Inconsistent data, existing Zero allocation identified for {}'
            #         err_list.append(msg.format(sr_obj.storage_product))
            if sr_obj.storage_product in parent_sp_map:
                msg = 'in-consistent data, Product {} not unique in request {}'
                err_list.append(msg.format(sr_obj.storage_product, existing_request_obj))
            parent_sp_map[sr_obj.storage_product] = sr_obj

        # calculate current_quota, storage product must be unique in Request
        curr_sp_list = list()
        for sr_dict in input_storage_requests:
            sp = fetch_storage_product(sr_dict.get('storage_product'))
            if sp in curr_sp_list:
                msg = '{} must be unique per Request'
                raise ValidationError(msg.format(sp))
            curr_sp_list.append(sp)
            current_quota = float(0)
            if sp in parent_sp_map:
                parent_sr = parent_sp_map.pop(sp)
                current_quota = parent_sr.current_quota
                if existing_request_obj.request_status.code == \
                        db.REQUEST_STATUS_PROVISIONED:
                    current_quota = parent_sr.approved_quota_total
                sr_dict['parent_sr'] = parent_sr
            sr_dict['current_quota'] = current_quota
            if sr_dict['current_quota'] == 0 and sr_dict['requested_quota_change'] == 0:
                # check if request has been intentionally zero'd out previously
                if sr_dict['approved_quota_total'] == 0:
                    continue
                msg = 'Zero allocation request not permitted for {}'
                err_list.append(msg.format(sp))

        pd_context = StorageRequestSerializer.show_error_msg_context()
        for sp, sr_remaining in parent_sp_map.items():
            if crams_action_state.is_update_action and \
                    self.ignore_existing_storage_request(
                        sr_remaining, is_admin_action):
                continue
            new_sr = copy.copy(sr_remaining)
            new_sr.id = None
            sz = StorageRequestSerializer(new_sr, context=pd_context)
            sr_dict = sz.data
            sr_dict['parent_sr'] = sr_remaining
            sr_dict['current_quota'] = sr_remaining.current_quota
            input_storage_requests.append(sr_dict)

        if err_list:
            raise ValidationError(err_list)
        return validate_storage_requests(input_storage_requests)

    def add_validate_question_response(self, qr_list):
        if not qr_list:
            crams_action_state = self.get_action_state()
            if crams_action_state.is_partial_action:
                existing_instance = self.get_action_state_instance()
                if existing_instance:
                    sz_class = question_serializers.RequestQuestionResponseSerializer
                    obj_list = existing_instance.request_question_responses.all()
                    return sz_class(obj_list, many=True).data
            return list()
        return qr_list

    @classmethod
    def ignore_existing_storage_request(
            cls, existing_storage_request_obj, is_admin_action=False):
        sr_status = existing_storage_request_obj.request.request_status.code
        if sr_status == db.REQUEST_STATUS_PROVISIONED:
            if existing_storage_request_obj.approved_quota_total == 0:
                # Allocation reduced to Zero, remove from new Transaction
                return True
        elif sr_status in db.EDIT_STATUS and not is_admin_action:
            # New Product Request can be removed before Approval
            if existing_storage_request_obj.current_quota == 0:
                return True
        return False

    def get_action_state_instance(self):
        return self.get_action_state().existing_instance

    def validate(self, data):
        """validate.

        :param data:
        :return validated_data:
        """
        crams_action_state = self.get_action_state()
        instance = self.get_action_state_instance()

        # validate and setup Node information for Allocation
        allocation_home_obj = data.get('allocation_home')
        if not allocation_home_obj and instance:
            allocation_home_obj = instance.allocation_home
        if allocation_home_obj:
            data['allocation_home'] = allocation_home_obj

        in_national_percent = data.get('national_percent')
        if not in_national_percent and instance:
            in_national_percent = instance.national_percent
        data['national_percent'] = self.validate_allocation_percentage(
            crams_action_state, in_national_percent, allocation_home_obj)

        # validate question responses
        question_response_data = self.initial_data.get('request_question_responses')
        data['request_question_responses'] = self.add_validate_question_response(question_response_data)

        # validate compute_requests, use initial_data for method_field
        compute_requests = self.initial_data.get('compute_requests', list())
        # call add_validate..., even if input compute_requests is empty
        data['compute_requests'] = \
            self.add_validate_related_compute_requests(compute_requests)

        # validate storage_requests use initial_data for method_field
        storage_requests = self.initial_data.get('storage_requests', list())
        # call add_validate..., even if input storage_requests is empty
        data['storage_requests'] = \
            self.add_validate_related_storage_requests(storage_requests)

        if crams_action_state.is_create_action:
            self.validate_min_max_related_objects(data)
            msg = 'One of e_research_system or funding_scheme is required.'
            if 'funding_scheme' not in data \
                    and 'e_research_system' not in data:
                raise ValidationError({
                    'e_research_system': msg
                })

        if self.instance and crams_action_state.is_draft_status_requested:
            status = self.instance.request_status
            msg = 'Draft status not allowed for request in status: '
            if status.code not in db.DRAFT_PERMISSIBLE_STATES:
                raise ValidationError(msg + status.status)

        if crams_action_state.is_partial_action:
            if (crams_action_state.override_data and 'request_status' in
                    crams_action_state.override_data):
                in_status_code = crams_action_state.override_data['request_status']
                existing_status_code = instance.request_status.code

                if in_status_code in db.LEGACY_STATES or existing_status_code in db.LEGACY_STATES:
                    raise ValidationError('Request Status : legacy states \
                                          partial update not implemented yet \
                                          {}/{}'.format(in_status_code,
                                                        existing_status_code))

                if in_status_code not in db.ADMIN_STATES:
                    raise ValidationError('Request Status {}: partial update \
                                          denied, Not an Admin action'
                                          .format(in_status_code))

                if existing_status_code == in_status_code:
                    raise ValidationError(
                        'Request Status: Action cancelled current state is '
                        'same as new state {}'.format(
                            instance.request_status.status))

                elif existing_status_code in db.DECLINED_STATES:
                    if in_status_code not in [db.REQUEST_STATUS_UPDATE_OR_EXTEND, db.REQUEST_STATUS_SUBMITTED]:
                        raise ValidationError('Request Status: Declined \
                                               applications can only move \
                                               to edit states')
                    elif (in_status_code != db.REQUEST_STATUS_UPDATE_OR_EXTEND
                          and existing_status_code ==
                          db.REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED):
                        raise ValidationError('Request Status: requests in \
                                              extend_decline_status can only \
                                              move to update_or_extend status')

                    elif (existing_status_code == db.REQUEST_STATUS_DECLINED and
                          in_status_code != db.REQUEST_STATUS_SUBMITTED):
                        raise ValidationError('Request Status: requests in \
                                              declined status can only move \
                                              to submitted status')

        elif crams_action_state.is_update_action:
            # partial action can also be an update action, to ensure partial
            # action is actioned instead of code below, do not move this elif
            self.validate_min_max_related_objects(data)

        # new_request_status and save_new
        current_request = data.pop('current_request', None)
        if current_request:
            raise ParseError('Requests with current_request value set \
                             are historic, readonly records. Update fail')

        data['allocation_extension_count'] = 0
        existing_request_instance = self.instance
        if existing_request_instance:
            erb_system = existing_request_instance.e_research_system
            data['allocation_extension_count'] = \
                existing_request_instance.allocation_extension_count
        else:
            erb_system = None

        if existing_request_instance:
            project = existing_request_instance.project
            current_contact = self.contact
            if self.project_contact_has_readonly_access(
                    project, current_contact, erbs=erb_system):
                msg = 'User does not have update access on Project '
                raise PermissionDenied(msg + project.title)

        # set funding scheme and/or e_research_system
        funding_scheme = data.get('funding_scheme', None)
        e_research_system = data.get('e_research_system')
        if not crams_action_state.is_create_action:
            # partial update or Clone
            if not funding_scheme:
                funding_scheme = existing_request_instance.funding_scheme
                if funding_scheme:
                    data['funding_scheme'] = funding_scheme

            if not e_research_system:
                e_research_system = existing_request_instance.e_research_system
                if e_research_system:
                    data['e_research_system'] = e_research_system

        # set Request Status, evaluate_save_new
        new_expected_request_status_instance, save_new = self.determine_new_status_save_new(
            crams_action_state, existing_request_instance, e_research_system, funding_scheme)

        data['request_status'] = new_expected_request_status_instance
        data['save_new'] = save_new

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        # Cannot update request being provisioned
        if (self.cramsActionState.is_update_action and
                self.instance.request_status.code in db.APPROVAL_STATES):
            if not (self.cramsActionState.is_partial_action and
                    self.cramsActionState.override_data):
                err_dict = {
                    'request id {}'.format(self.instance.id): 'Request cannot updated while being provisioned'
                }
                raise ValidationError(err_dict)
        new_request, new_save = self._save_request(validated_data, instance)

        # reset incorrectly set approved_quota
        valid_approved_quota__status = [db.REQUEST_STATUS_APPROVED,
                                        db.REQUEST_STATUS_PARTIAL_PROVISIONED,
                                        db.REQUEST_STATUS_PROVISIONED]
        if new_request.request_status.code in valid_approved_quota__status:
            pass
        else:
            for sr in new_request.storage_requests.all():
                if sr.approved_quota_change == 0:
                    pass
                else:
                    LOG.error('Approved quota reset for storage_Request {}'.format(sr))
                    sr.approved_quota_change = 0
                    sr.save()

        # update current_request property for the historic project, required to
        # identify list for history
        # skip this if updating an existing request
        if new_save:
            instance.current_request = new_request
            instance.save()
            Request.objects.filter(current_request=instance).update(
                current_request=new_request)

        return new_request

    @transaction.atomic
    def create(self, validated_data):
        """create.

        :param validated_data:
        :return new_request:
        """
        new_request, new_save = self._save_request(validated_data)
        return new_request

        # # setup default ERB project Ids for this request
        # user_erb_roles = self.get_provision_roles_for_user()
        # contact = self.contact
        # pid_config.update_erb_project_ids_for_key(
        #     new_request, user_erb_roles, contact)
        #
        # # setup default ERB request level Ids for this request
        # pid_config.update_erb_request_ids_for_key(
        #     new_request, user_erb_roles, contact)
        #
        # return new_request

    def determine_new_status_save_new(
            self, crams_action_state, existing_request_instance, e_research_system, funding_scheme):

        if e_research_system:
            request_system_name = e_research_system.name
        else:
            request_system_name = funding_scheme.funding_body.name

        # set Request Status
        new_expected_request_status_instance = self.evaluate_new_request_status(
            request_system_name, crams_action_state)
        if not new_expected_request_status_instance:
            raise ParseError('Request status could not be determined')

        save_new = True

        # checking for allocation field changes and override the evaluateRequestStatus
        # FOR R@CMON if the following fields has changes:
        #   - new storage product quota
        #   - existing storage product quota change
        # if the above changes in the allocation form then proceed to "Update/Extended" status

        # any other project/request meta data that is changed will also be moved
        # or updated to the "Application Updated" status
        # Note:
        # checking on request_system_name alone is not correct, need to include erb_name as well
        #  - TODO change EXTEND_ON_QUOTA_CHANGE to hold ERB System DB object instead of just erb system name
        if (request_system_name.lower() in allocation_config.EXTEND_ON_QUOTA_CHANGE and
                existing_request_instance):
            status_codes = [db.REQUEST_STATUS_PROVISIONED,
                            db.REQUEST_STATUS_APPLICATION_UPDATED,
                            db.REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED]

            if existing_request_instance.request_status.code in status_codes:
                # check quota has changed for any products
                # only if quota has change to do save new
                if not self.product_quota_change(existing_request_instance):
                    # application updated status
                    app_updated = RequestStatus.objects.get(
                        code=db.REQUEST_STATUS_APPLICATION_UPDATED)
                    new_expected_request_status_instance = app_updated

                    # if application updated status
                    if (existing_request_instance.request_status.code ==
                            db.REQUEST_STATUS_APPLICATION_UPDATED):
                        # do not clone it just updated the time stamp
                        save_new = False

            elif existing_request_instance.request_status.code == db.REQUEST_STATUS_UPDATE_OR_EXTEND:
                if new_expected_request_status_instance.code == db.REQUEST_STATUS_UPDATE_OR_EXTEND:
                    save_new = False

        return new_expected_request_status_instance, save_new

    def _save_request(self, validated_data, existing_request_instance=None):
        crams_action_state = self.cramsActionState
        if not crams_action_state:
            raise ParseError('CramsRequestSerializer.saveRequest: ActionState \
                             not found, contact tech support')

        current_contact = self.contact

        new_expected_request_status_instance = validated_data.get('request_status')
        save_new = validated_data.pop('save_new')

        # set the sent_ext_support_email flag
        if existing_request_instance:
            if existing_request_instance.request_status != new_expected_request_status_instance:
                validated_data['sent_ext_support_email'] = False

        # update full provision count
        validated_data['allocation_extension_count'] = 0
        if existing_request_instance:
            validated_data['allocation_extension_count'] = existing_request_instance.allocation_extension_count
            existing_status_code = existing_request_instance.request_status.code
            if existing_status_code == db.REQUEST_STATUS_PROVISIONED:
                if not new_expected_request_status_instance.code == existing_status_code:
                    validated_data['allocation_extension_count'] = \
                        existing_request_instance.allocation_extension_count + 1

        # set remaining fields
        current_user = self.get_current_user()
        validated_data['updated_by'] = current_user
        if crams_action_state.is_create_action:
            validated_data['created_by'] = current_user
            validated_data['approval_notes'] = None
        else:  # partial update  or Clone
            if 'start_date' not in validated_data:
                validated_data[
                    'start_date'] = existing_request_instance.start_date

            if 'end_date' not in validated_data:
                validated_data['end_date'] = existing_request_instance.end_date

            if 'project' not in validated_data:
                validated_data['project'] = existing_request_instance.project

            validated_data['creation_ts'] = existing_request_instance.creation_ts
            validated_data['created_by'] = existing_request_instance.created_by
            if crams_action_state.is_clone_action:
                validated_data[
                    'approval_notes'] = existing_request_instance.approval_notes
                validated_data['last_modified_ts'] = \
                    existing_request_instance.last_modified_ts
                validated_data[
                    'updated_by'] = existing_request_instance.updated_by
            elif new_expected_request_status_instance.code in db.NON_ADMIN_STATES:
                validated_data['approval_notes'] = None

            # copy across the previous data_sensitive flag
            if 'data_sensitive' not in validated_data:
                validated_data['data_sensitive'] = \
                    existing_request_instance.data_sensitive

        # creating/cloning a new request instance
        # update related fields
        related_many_fields_update_dict = {
            'request_question_responses': self.update_request_question_responses,
            'compute_requests': self.update_compute_requests,
            'storage_requests': self.update_storage_requests
        }
        # remove 'many related' data before saving request
        related_many_fields_data_dict = dict()
        for related_field in related_many_fields_update_dict.keys():
            related_field_data = validated_data.pop(related_field, None)
            related_many_fields_data_dict[related_field] = related_field_data

        # override save new, if parent project is different to existing request
        project = validated_data.get('project')
        if existing_request_instance:
            if not save_new:
                if not existing_request_instance.project == project:
                    save_new = True

        if save_new:
            request = Request.objects.create(**validated_data)
        else:
            # set existingRequestInstance as request
            request = existing_request_instance

            request.data_sensitive = validated_data.get('data_sensitive')
            request.national_percent = validated_data.get('national_percent')
            fund_scheme = validated_data.get('funding_scheme')
            if fund_scheme:
                request.funding_scheme_id = fund_scheme.id
            else:
                request.funding_scheme = None
            # e_research_system cannot be updated for existing requests
            alloc_home = validated_data.get('allocation_home')
            if alloc_home:
                request.allocation_home_id = alloc_home.id
            else:
                request.allocation_home = None
            request.start_date = validated_data.get('start_date')
            request.end_date = validated_data.get('end_date')
            request.approval_notes = validated_data.get('approval_notes')
            request.sent_email = validated_data.get('sent_email')
            request.updated_by = validated_data.get('updated_by')
            request.save()

            self.context[CRAMS_REQUEST_PARENT] = request

        # update transaction id
        request.transaction_id = self.determine_transaction_id_for_request(
            request, existing_request_instance)
        request.save()

        # Fetch request data to log
        field_fn_dict = {
            'allocation_home': None,
            'data_sensitive': None,
            'national_percent': None,
            'approval_notes': None,
            'funding_scheme': lambda obj: obj.funding_scheme if obj is not None else None
        }
        changed_request_fields_set, _, _ = log_process.generate_before_after_json(
            existing_request_instance, validated_data, check_field_extract_fn_dict=field_fn_dict)
        changed_fields_set = set()
        if changed_request_fields_set:
            changed_fields_set = {'Changed: Allocation[' + ','.join(changed_request_fields_set) + ']'}

        request_data = dict()
        request_data['request_obj'] = request
        request_data['crams_action_state'] = crams_action_state
        request_data['save_new'] = save_new
        request_data['current_user'] = current_user
        request_data['existing_request_instance'] = existing_request_instance
        request_data['changed_fields_set'] = changed_fields_set
        for k, v in related_many_fields_data_dict.items():
            request_data[k] = v
        for related_field, update_fn in related_many_fields_update_dict.items():
            if update_fn:
                update_fn(related_field, request_data)

        # log if data has changed, both for create and update of project
        if changed_fields_set:
            if not existing_request_instance:
                log_message = 'New Allocation Request'
                if request.request_status.code == db.DRAFT_STATES:
                    log_message = 'New Draft Allocation Request'
            else:
                log_message = ','.join(changed_fields_set)
                # before_json, after_json, user_obj, allocation_request, message, contact=None
            RequestMetaLogger.build_allocation_metadata_change_json(
                request, existing_request_instance, current_user, message=log_message,
                contact=current_contact, sz_context=self.context)
        print('---- before email processing fn ....')
        email_processing_fn = allocation_config.get_email_processing_fn(
            allocation_config.ERB_System_Allocation_Submit_Email_fn_dict, request.e_research_system)

        print('---- after email processing fn ....{}'.format(email_processing_fn))
        if email_processing_fn:
            is_clone_action = crams_action_state.is_clone_action
            email_sent = email_processing_fn(
                existing_request_instance, request, serializer_context=self.context, is_clone_action=is_clone_action)
            if email_sent and existing_request_instance:
                # set sent_email flag
                self.get_sent_email_from_context(
                    self.context, existing_request_instance.id, request)

        return request, save_new

    @classmethod
    def update_request_question_responses(cls, related_field, request_data):
        """

        :param related_field:
        :param request_data:
        :return:
        """

        def changed_msg(questions_set, msg):
            ret_msg = msg
            for pqr_tuple in questions_set:
                question, new_response, existing_response = pqr_tuple
                ret_msg += question.key + ','
            return ret_msg

        request = request_data.get('request_obj')
        existing_request_instance = request_data.get('existing_request_instance')
        changed_fields_set = request_data.get('changed_fields_set')

        req_question_responses_data = request_data.get(related_field)

        # fetch the question id based on key
        # the question could change but still use the old id
        for qr in req_question_responses_data:
            qu = Question.objects.filter(key=qr.get('question').get('key')).first()
            if qu:
                qr['question']['id'] = qu.id

        ret_changed_obj = \
            question_serializers.RequestQuestionResponseSerializer.save_request_question_response(
                req_question_responses_data, new_parent=request, old_parent=existing_request_instance)

        if ret_changed_obj.err_list:
            raise ValidationError(ret_changed_obj.err_list)

        changed_list = list()
        if ret_changed_obj.modified_related_field_set:
            base_msg = 'modified: '
            changed_list.append(changed_msg(ret_changed_obj.modified_related_field_set, base_msg))
        if ret_changed_obj.new_related_field_set:
            base_msg = 'added new: '
            changed_list.append(changed_msg(ret_changed_obj.new_related_field_set, base_msg))
        if ret_changed_obj.removed_related_field_set:
            base_msg = 'removed: '
            changed_list.append(changed_msg(ret_changed_obj.removed_related_field_set, base_msg))
        if changed_list:
            change_msg = 'Request_questions: ' + ' && '.join(changed_list)
            changed_fields_set.add(change_msg)
        return ret_changed_obj

    @classmethod
    def product_changed_field(
            cls, parent_prod_req, prod_req_serializer, fields_to_check, prod_field_name):
        def changed_msg(data_set, msg):
            if not data_set:
                return None
            return msg + ': ' + ','.join(data_set)

        product_changed_dict = dict()
        # identify changed product requests
        ret_changed_obj = log_validation_utils.ChangedMetadata()
        changed_list = list()
        for field in fields_to_check:
            new_field_data = prod_req_serializer.validated_data.get(field)
            if parent_prod_req:
                if getattr(parent_prod_req, field) == new_field_data:
                    continue

            product_changed_set = ret_changed_obj.modified_related_field_set
            if not parent_prod_req:
                product_changed_set = ret_changed_obj.new_related_field_set
            elif not prod_req_serializer:
                product_changed_set = ret_changed_obj.removed_related_field_set
            product_changed_set.add(field)

        if ret_changed_obj.modified_related_field_set:
            base_msg = 'modified: '
            changed_list.append(changed_msg(ret_changed_obj.modified_related_field_set, base_msg))
        if ret_changed_obj.new_related_field_set:
            base_msg = 'added new: '
            changed_list.append(changed_msg(ret_changed_obj.new_related_field_set, base_msg))
        if ret_changed_obj.removed_related_field_set:
            base_msg = 'removed: '
            changed_list.append(changed_msg(ret_changed_obj.removed_related_field_set, base_msg))

        prod = prod_req_serializer.validated_data.get(prod_field_name)
        if prod not in product_changed_dict:
            product_changed_dict[prod] = changed_list

        changed_fields_set = set()
        if product_changed_dict:
            for k, v in product_changed_dict.items():
                if v:
                    changed_fields_set.add('{}: {}'.format(k, v))
        return changed_fields_set

    def update_compute_requests(self, related_field, request_data):
        def check_changed_fields(parent_prod_req, prod_req_serializer, changed_fields_set):
            cr_changed_fields = self.product_changed_field(
                parent_prod_req, prod_req_serializer, fields_to_check, 'compute_product')
            if cr_changed_fields:
                changed_fields_set |= cr_changed_fields

        compute_requests = request_data.get(related_field)
        request_obj = request_data.get('request_obj')
        existing_request_instance = request_data.get('existing_request_instance')
        project = request_obj.project
        current_user = request_data.get('current_user')
        crams_action_state = request_data.get('crams_action_state')
        changed_fields_set_in = request_data.get('changed_fields_set')

        fields_to_check = ['instances', 'approved_instances', 'cores',
                           'approved_cores', 'core_hours', 'approved_core_hours']

        prod_serializer = ProductRequestSerializer(context=self.context)
        pd_fn = ProductRequestSerializer.propagate_provision_details
        if compute_requests:
            for parent_cr, compute_req_serializer in compute_requests:
                # update existing instance, if not creating a new Request Serializer
                if request_obj == existing_request_instance:
                    if parent_cr:
                        # check changed fields before updating existing compute request
                        check_changed_fields(parent_cr, compute_req_serializer, changed_fields_set_in)
                        for field in fields_to_check:
                            new_val = compute_req_serializer.validated_data.get(field)
                            setattr(parent_cr, field, new_val)
                        parent_cr.save()
                        continue
                    else:
                        # if no parent_sr, this is a new product, create using serializer next
                        pass

                # ensure request is overridden with current request
                cr_obj = compute_req_serializer.save(request=request_obj)
                if parent_cr:
                    if not compute_req_serializer.reset_provision_details(cr_obj):
                        cr_obj.provision_details = pd_fn(parent_cr)
                        cr_obj.save()
                if crams_action_state.is_create_action:
                    prod_serializer.set_applicant_default_role(
                        project, current_user, cr_obj.compute_product)
                check_changed_fields(parent_cr, compute_req_serializer, changed_fields_set_in)

    def update_storage_requests(self, related_field, request_data):
        def check_changed_fields(parent_prod_req, prod_req_serializer, changed_fields_set):
            fields_to_check = {'requested_quota_change', 'approved_quota_change'}
            if parent_sr:
                if existing_request_instance.request_status.code == db.REQUEST_STATUS_PROVISIONED:
                    fields_to_check.remove('approved_quota_change')
                    if not current_quota:
                        fields_to_check.remove('requested_quota_change')
            else:  # new product request
                fields_to_check.remove('approved_quota_change')

            sr_changed_fields = self.product_changed_field(
                parent_prod_req, prod_req_serializer, fields_to_check, 'storage_product')
            if sr_changed_fields:
                changed_fields_set |= sr_changed_fields

        storage_requests = request_data.get(related_field)
        request_obj = request_data.get('request_obj')
        project = request_obj.project
        current_user = request_data.get('current_user')
        existing_request_instance = request_data.get('existing_request_instance')
        crams_action_state = request_data.get('crams_action_state')
        changed_fields_set_in = request_data.get('changed_fields_set')

        prod_serializer = ProductRequestSerializer(context=self.context)
        pd_fn = ProductRequestSerializer.propagate_provision_details

        if storage_requests:
            for sr_tuple in storage_requests:
                parent_sr, sr_serializer, current_quota = sr_tuple
                # update existing instance, if not creating a new Request Serializer
                if request_obj == existing_request_instance:
                    if parent_sr:
                        check_changed_fields(
                            parent_sr, sr_serializer, changed_fields_set_in)  # do before updating existing parent
                        parent_sr.current_quota = current_quota
                        parent_sr.approved_quota_change = sr_serializer.validated_data.get('approved_quota_change')
                        parent_sr.requested_quota_change = sr_serializer.validated_data.get('requested_quota_change')
                        # TODO: manage ProductQuestion responses, currently none for DD (HPC??)
                        parent_sr.save()
                        continue
                    else:
                        # check if this sr storage product has changed by fetching what is currently in db
                        try:
                            sr_id = sr_serializer.initial_data.get('id')
                            sr_obj = StorageRequest.objects.get(pk=sr_id)
                            if sr_obj.storage_product != sr_serializer.validated_data.get('storage_product'):
                                sr_obj.storage_product = sr_serializer.validated_data.get('storage_product')
                                sr_obj.save()
                                continue
                        except:
                            pass
                        # if no parent_sr, this is a new product, create using serializer next
                        pass
                # ensure request is overridden with current request
                if current_quota:
                    sr_serializer.validated_data['current_quota'] = current_quota
                sr_obj = sr_serializer.save(request=request_obj)
                if crams_action_state.is_create_action:
                    prod_serializer.set_applicant_default_role(
                        project, current_user, sr_obj.storage_product)
                if parent_sr:
                    sr_obj.provision_id = parent_sr.provision_id
                    if not sr_serializer.reset_provision_details(sr_obj):
                        sr_obj.provision_details = pd_fn(parent_sr)
                    sr_obj.save()
                check_changed_fields(parent_sr, sr_serializer, changed_fields_set_in)
                # TODO: manage related ProductQuestion responses, currently none for DD (HPC??)

    @classmethod
    def get_sent_email_from_context(cls, context, req_id, request):
        try:
            req_list = context['request'].data['requests']
            req = next((req for req in req_list if req['id'] == req_id), None)

            if req:
                request.sent_email = req['sent_email']
        except:
            pass

    @classmethod
    def determine_transaction_id_for_request(
            cls, current_req, historical_request):
        is_new_transaction = True
        new_transaction_status_list = [db.REQUEST_STATUS_PROVISIONED,
                                       db.REQUEST_STATUS_APPLICATION_UPDATED]
        if historical_request:
            existing_status = historical_request.request_status.code
            if existing_status not in new_transaction_status_list:
                is_new_transaction = False
            if (current_req.request_status.code ==
                    db.REQUEST_STATUS_APPLICATION_UPDATED):
                is_new_transaction = False
        if is_new_transaction:
            return transaction_id_config.get_new_transaction_id(
                current_req, historical_request)

        return historical_request.transaction_id

    # Detects any change in the storage request quota
    # returns True if positive for changes and False if not
    def product_quota_change(self, existing_request_instance):
        # compare the number of storage requests in existing and new
        if not existing_request_instance:
            return True

        count_existing_sr = len(existing_request_instance.storage_requests.all())
        if existing_request_instance.request_status.code == db.REQUEST_STATUS_PROVISIONED:
            for sr in existing_request_instance.storage_requests.all():
                if sr.approved_quota_total == 0 and sr.approved_quota_change == 0:  # dropped products, do not include
                    count_existing_sr = count_existing_sr - 1

        prev_status_xdecline = \
            existing_request_instance.request_status.code == db.REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED

        new_sr_list = self.initial_data.get('storage_requests')
        count_new_sr = len(new_sr_list)
        if count_existing_sr != count_new_sr:
            return True

        new_sr_dict = dict()
        if new_sr_list:
            for new_sr in new_sr_list:
                prod_id = new_sr['storage_product']['id']
                new_sr_dict[prod_id] = new_sr

        # check is storage request quota for any changes
        for existing_sr in existing_request_instance.storage_requests.all():
            # get storage requests new request
            new_sr = new_sr_dict.get(existing_sr.storage_product.id)
            if new_sr:
                if prev_status_xdecline:
                    if new_sr.get('requested_quota_change') != 0:
                        return True
                elif new_sr.get('requested_quota_total') != existing_sr.requested_quota_total:
                    return True
            else:
                # existing sr storage product not found in new sr, likley to be changed or removed
                return True

        # TODO: compute quota change

        # if all checks did not find any changes return "False" for no changes detected
        return False

    @classmethod
    def evaluate_new_request_status(cls, request_system_name, crams_action_state):
        if not crams_action_state:
            raise ParseError('CramsActionState required')

        if crams_action_state.is_create_action:
            status_code = db.REQUEST_STATUS_SUBMITTED
            if crams_action_state.is_draft_status_requested:
                status_code = db.REQUEST_STATUS_NEW
            return RequestStatus.objects.get(code=status_code)

        existing_request = crams_action_state.existing_instance
        if existing_request and crams_action_state.is_draft_status_requested:
            # Draft is permitted only for requests in DRAFT_PERMISSIBLE_STATES
            existing_status = existing_request.request_status.code
            if existing_status in db.DRAFT_PERMISSIBLE_STATES:
                if existing_status == db.REQUEST_STATUS_NEW:
                    return existing_request.request_status
                status_code = db.REQUEST_STATUS_EXTEND_DRAFT
                return RequestStatus.objects.get(code=status_code)

        move_to_extend_status_codes = [
            db.REQUEST_STATUS_UPDATE_OR_EXTEND,
            db.REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED,
            db.REQUEST_STATUS_PROVISIONED]
        if crams_action_state.is_clone_action:
            status_code = existing_request.request_status.code
        elif (crams_action_state.override_data and
              'request_status' in crams_action_state.override_data):
            status_code = crams_action_state.override_data['request_status']
        elif (existing_request.request_status.code ==
              db.REQUEST_STATUS_NEW or
              existing_request.request_status.code ==
              db.REQUEST_STATUS_DECLINED):
            status_code = db.REQUEST_STATUS_SUBMITTED
        elif (existing_request.request_status.code in
              move_to_extend_status_codes):
            status_code = db.REQUEST_STATUS_UPDATE_OR_EXTEND
        elif existing_request.request_status.code == db.REQUEST_STATUS_APPLICATION_UPDATED:
            status_code = db.REQUEST_STATUS_UPDATE_OR_EXTEND
        else:
            status_code = existing_request.request_status.code

        return RequestStatus.objects.get(code=status_code)


def get_request_contact_email_ids(allocation_request):
    ret_set = set()
    for project_contact in allocation_request.project.project_contacts.all():
        ret_set.add(project_contact.contact.email)

    # Fix for missing applicant notification. Applicants are not added
    # to contacts until after Notifications are sent at create time.
    if allocation_request.updated_by.email not in ret_set:
        ret_set.add(allocation_request.updated_by.email)

    return list(ret_set)
