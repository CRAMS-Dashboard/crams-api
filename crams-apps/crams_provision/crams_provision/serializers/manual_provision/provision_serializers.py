# coding=utf-8
"""

"""

import logging
import pprint

from crams.constants.api import DO_NOT_OVERRIDE_PROVISION_DETAILS
from crams.constants.api import OVERRIDE_READONLY_DATA
from crams.models import ProvisionDetails
from crams.serializers.model_serializers import PrimaryKeyLookupField
from crams.serializers.provision_details_serializer import AbstractProvisionDetailsSerializer
from crams.serializers.provision_details_serializer import ReadOnlyProvisionDetailSerializer
from crams.utils.role import AbstractCramsRoleUtils
from crams_allocation.constants.db import REQUEST_STATUS_APPROVED
from crams_allocation.constants.db import REQUEST_STATUS_LEGACY_APPROVED
from crams_allocation.constants.db import REQUEST_STATUS_PROVISIONED
from crams_allocation.models import Request, NotificationTemplate
from crams_allocation.product_allocation.models import ComputeRequest, StorageRequest
from crams_allocation.serializers.request_serializers import CramsRequestWithoutProjectSerializer
from crams_allocation.serializers.project_request_serializers import ReadOnlyProjectRequestSerializer
from crams_allocation.serializers.request_serializers import ReadOnlyCramsRequestWithoutProjectSerializer
from crams_allocation.utils import request_utils
from crams_collection.models import Project, ProjectProvisionDetails
from crams_collection.serializers.provision_details import CollectionProvisionDetailsSerializer
from crams_collection.utils import project_user_utils
from crams_compute.models import ComputeProduct
from crams_compute.serializers.compute_product import AllocationComputeProductValidate
from crams_contact.models import Contact
from crams_contact.serializers import base_contact_serializer
from crams_storage.models import StorageProduct
from crams_storage.serializers.storage_product_serializers import StorageProductZoneOnlySerializer
from django.db import transaction
from django.db.models import Q
from rest_framework import exceptions
from rest_framework import serializers

from crams_provision.log.provision_log import ProvisionMetaLogger
from crams_provision.serializers import user_id_provision
from crams_provision.utils import provision_utils

PROVISION_ENABLE_REQUEST_STATUS = [
    REQUEST_STATUS_APPROVED, REQUEST_STATUS_LEGACY_APPROVED]

"""
Create a new user for provider  @ http://localhost:8000/admin/auth/user/
  user p001 with password p123  (id set to 15 in migrations,
  so ensure this id is relevant)

Create Crams user, with user id p001

Update Provider and set user for
  Nectar @ http://localhost:8000/admin/api/provider/9/
  select crams user created above 'p001'
  set user active
  ensure provider is set to NeCTAR
  save
  login to API with user p001

"""

LOG = logging.getLogger(__name__)


def fetch_project_provision_list_for_provider(project_obj, provider_list):
    """Fetch project provision list for provider."""
    # TODO refactor: provider has been removed from provision_details
    return project_obj.linked_provisiondetails.all()


def new_provision_detail(current_user, status=ProvisionDetails.SENT):
    return ProvisionDetails.objects.create(
        created_by=current_user,
        updated_by=current_user,
        status=status)

    ##############################################
    # API 1 :  List Products for provisioning    #
    ##############################################


class ProvisionProjectSerializer(ReadOnlyProjectRequestSerializer):
    def get_contact_system_ids(self, project_obj):
        qs = Contact.objects.filter(project_contacts__project=project_obj)
        sz_class = user_id_provision.ProvisionedContactSystemIdentifiers
        return sz_class(qs.distinct(), context=self.context, many=True).data

    """class ProvisionProjectSerializer."""

    def filter_provision_project(self, project_obj):
        """

        :param project_obj:
        :return:
        """
        ret_list = []

        current_user, context = project_user_utils.get_current_user_from_context(self)
        if not AbstractCramsRoleUtils.is_user_a_provider(current_user):
            return ret_list

        pd_context = AbstractProvisionDetailsSerializer.show_error_msg_context()

        status_filter_set = ProvisionDetails.READY_TO_SEND_SET

        context_request = context.get('request')
        new_only = context_request.query_params.get('new_request', None)
        if not new_only:
            status_filter_set = \
                status_filter_set.union(ProvisionDetails.SET_OF_SENT)

        provider_list = AbstractCramsRoleUtils.get_authorised_provider_list(current_user)
        if not provider_list:
            raise exceptions.ValidationError('User is not a provider')
        provider_provision_details = fetch_project_provision_list_for_provider(
            project_obj, provider_list)
        if not provider_provision_details.exists():  # new Project
            project_provision = ProjectProvisionDetails(project=project_obj)
            new_project_pd = new_provision_detail(
                current_user, status=ProvisionDetails.SENT)
            project_provision.provision_details = new_project_pd
            project_provision.save()
            status_filter_set.union(ProvisionDetails.SENT)

        query_set = provider_provision_details.filter(
            provision_details__status__in=status_filter_set)
        for pp in query_set.all():
            pd = pp.provision_details
            if pd.status == ProvisionDetails.POST_PROVISION_UPDATE:
                pd.status = ProvisionDetails.POST_PROVISION_UPDATE_SENT
                pd.save()
            pd_serializer = CollectionProvisionDetailsSerializer(pd, context=pd_context)
            ret_list.append(pd_serializer.data)
        return ret_list

    def filter_requests(self, project_obj):
        """filter requests."""
        ret_list = []

        current_user, context = project_user_utils.get_current_user_from_context(self)
        if not AbstractCramsRoleUtils.is_user_a_provider(current_user):
            return ret_list

        context_request = context.get('request')
        query_params = context_request.query_params
        request_id = query_params.get('request_id', None)
        if request_id:
            # , current_request__isnull=True)
            requests = project_obj.requests.filter(id=request_id)
        else:
            requests = project_obj.requests.filter(
                current_request__isnull=True)

        requests = requests.filter(
            request_status__code=REQUEST_STATUS_APPROVED)

        providers = AbstractCramsRoleUtils.get_authorised_provider_list(current_user)
        provider_filter = \
            Q(compute_requests__compute_product__provider__in=providers) \
            | Q(storage_requests__storage_product__provider__in=providers)

        for req in requests.filter(provider_filter).distinct():
            req_json = ProvisionRequestSerializer(
                req, context=self.context).data
            if req_json:
                if ('compute_requests' in req_json and
                    len(req_json['compute_requests']) > 0) or \
                        ('storage_requests' in req_json and
                         len(req_json['storage_requests']) > 0):
                    ret_list.append(req_json)

        return ret_list


class ProvisionRequestSerializer(ReadOnlyCramsRequestWithoutProjectSerializer):
    request_status = serializers.SerializerMethodField()
    compute_requests = serializers.SerializerMethodField(
        method_name='filter_compute_requests')
    storage_requests = serializers.SerializerMethodField(
        method_name='filter_storage_requests')
    approver_email = serializers.SerializerMethodField()
    partial_provision_flag = serializers.SerializerMethodField()

    class Meta(object):
        model = Request
        fields = ['id', 'funding_scheme', 'funding_body', 'e_research_system', 'request_status',
                  'transaction_id', 'compute_requests', 'storage_requests', 'approver_email',
                  'approval_notes', 'partial_provision_flag']

    @classmethod
    def get_request_status(cls, request_obj):
        return request_utils.get_erb_request_status_dict(request_obj)

    @classmethod
    def get_approver_email(cls, request_obj):
        return request_utils.get_request_approver_email(request_obj)

    @classmethod
    def get_partial_provision_flag(cls, request_obj):
        return request_utils.get_partial_provision_flag(request_obj)

    @classmethod
    def provision_required(cls, product_request):
        if isinstance(product_request, StorageRequest):
            if product_request.approved_quota_change > 0:
                return True
        return False

    def _filter_common(self, base_query_set, get_representation_fn):
        ret_list = []

        current_user, context = project_user_utils.get_current_user_from_context(self)
        if not AbstractCramsRoleUtils.is_user_a_provider(current_user):
            return ret_list

        context_request = context.get('request')
        new_only = context_request.query_params.get('new_request', None)
        filter_provisioned = \
            context_request.query_params.get('filter_provisioned', None)
        query_set = base_query_set

        query_filter = Q()
        if filter_provisioned or new_only:
            query_filter = Q(provision_details__isnull=True) | Q(
                provision_details__status__in=ProvisionDetails.READY_TO_SEND_SET)
            if not new_only:
                query_filter = query_filter | Q(
                    provision_details__status__in=ProvisionDetails.SET_OF_SENT)
        query_set = query_set.filter(query_filter)

        valid_providers = AbstractCramsRoleUtils.get_authorised_provider_list(current_user)
        if base_query_set.model == ComputeRequest:
            query_set = query_set.filter(
                compute_product__provider__in=valid_providers)
        elif base_query_set.model == StorageRequest:
            query_set = query_set.filter(
                storage_product__provider__in=valid_providers)

        for productRequest in query_set:
            ret_list.append(get_representation_fn(productRequest))
            provision_details = productRequest.provision_details
            update_status = ProvisionDetails.READY_TO_SEND_SET
            update_sent_status = ProvisionDetails.POST_PROVISION_UPDATE_SENT

            if provision_details:
                if provision_details.status in update_status:
                    provision_details.status = update_sent_status
                    provision_details.save()
            else:
                # new Product Request
                # - Create new Sent Provision details for Product Request
                pd = new_provision_detail(current_user)
                productRequest.provision_details = pd
                productRequest.save()

        return ret_list

    def filter_compute_requests(self, request_obj):
        """filter compute requests."""

        def get_representation_fn(compute_request_obj):
            """get representation fn."""
            product = compute_request_obj.compute_product
            return {
                'id': compute_request_obj.id,
                'product': {'id': product.id, 'name': product.name},
                'approved_instances': compute_request_obj.approved_instances,
                'approved_cores': compute_request_obj.approved_cores,
                'approved_core_hours': compute_request_obj.approved_core_hours
            }

        return self._filter_common(
            request_obj.compute_requests,
            get_representation_fn)

    def filter_storage_requests(self, request_obj):
        """filter storage requests."""

        def get_representation_fn(storage_request_obj):
            """get representation fn."""
            product_dict = StorageProductZoneOnlySerializer(
                storage_request_obj.storage_product).data
            ret_data = {
                'id': storage_request_obj.id,
                'product': product_dict,
                'approved_quota_change': storage_request_obj.approved_quota_change,
                'current_quota': storage_request_obj.current_quota,
                'approved_quota_total': storage_request_obj.approved_quota_total
            }
            if storage_request_obj.provision_details:
                ret_data['provision_details'] = \
                    ReadOnlyProvisionDetailSerializer(storage_request_obj.provision_details).data

            if storage_request_obj.provision_id:
                ret_data['provision_id'] = \
                    storage_request_obj.provision_id.provision_id

            return ret_data

        return self._filter_common(
            request_obj.storage_requests, get_representation_fn)


##############################################
#   API 2 :  Update Provisioning Result      #
##############################################
class UpdateOnlySerializer(serializers.Serializer):
    """class UpdateOnlySerializer."""

    def pprint(self, obj):
        """print."""
        if not hasattr(self, 'pp'):
            self.pp = pprint.PrettyPrinter(indent=4)  # For Debug
        self.pp.pprint(obj)

    def create(self, validated_data):
        """create."""
        raise exceptions.ParseError('Create not allowed ')


class BaseProvisionSerializer(UpdateOnlySerializer):
    """class BaseProvisionSerializer."""

    id = serializers.IntegerField()

    def validate(self, data):
        """validate."""
        if not id:
            raise exceptions.ValidationError({'id': 'This field is required.'})
        return data

    def get_current_user(self):
        user, _ = project_user_utils.get_current_user_from_context(self)
        if not user:
            raise exceptions.ValidationError({
                'message': 'Unable to determine current user for api request'})
        return user

    def validate_user_is_provider(self):
        """validate user is provider."""
        return AbstractCramsRoleUtils.is_user_a_provider(self.get_current_user())

    def validate_user_provisions_product(self, product):
        """validate user provisions product."""
        contact = base_contact_serializer.get_serializer_user_contact(self)
        if project_user_utils.is_contact_product_provider(contact, product):
            return True
        raise exceptions.ValidationError(
            {'message': 'User {} is not a provider for product {}'.format(
                contact.email, repr(product))})


class BaseProvisionMessageSerializer(BaseProvisionSerializer):
    """class BaseProvisionMessageSerializer."""

    message = serializers.CharField(
        max_length=9999, allow_null=True, allow_blank=True, required=False)
    success = serializers.BooleanField()
    resend = serializers.BooleanField(required=False)

    def validate(self, data):
        """validate."""
        #        super(BaseProvisionProductSerializer, self).validate(data)
        if not data.success and not data.message:
            raise exceptions.ValidationError(
                {'message': 'This field is required when success is false'})
        return data

    @classmethod
    def get_erb_system_template(cls, erbs, erb_system_key_obj):
        try:
            return NotificationTemplate.objects.filter(
                system_key=erb_system_key_obj, e_research_system=erbs,
                request_status__isnull=True).first()
        except NotificationTemplate.DoesNotExist:
            pass
        return None

    # @classmethod
    # def send_contact_id_email(cls, project, erb_contact_id_list):
    #     for erb_contactid in erb_contact_id_list:
    #         # get the ERBS from project to get template
    #         erbs = project.requests.first().e_research_system
    #         template = cls.get_erb_system_template(erbs, erb_contactid.system)
    #
    #         if not template:
    #             msg = 'Notification Template not defined for {}'
    #             LOG.warning(msg.format(erb_contactid.system))
    #             return
    #
    #         cls.process_notification_template(project,
    #                                           template,
    #                                           erb_contactid)

    # @classmethod
    # def process_notification_template(cls, project, template_obj,
    #                                   erb_contactid):
    #     template = template_obj.template_file_path
    #     erb_name = erb_contactid.system.e_research_body.name
    #     subject = erb_name + ': User Provisioning'
    #     contact_email = erb_contactid.contact.email
    #     prj_id = ProjectID.objects.get(project=project)
    #     mail_content = {"erb_contactid": erb_contactid,
    #                     "project": project,
    #                     "project_id": prj_id}
    #     try:
    #         recipient_list = [contact_email]
    #         reply_to = eSYSTEM_REPLY_TO_EMAIL_MAP.get(
    #             strip_lower(erb_name), None)
    #         send_email_notification.delay(
    #             sender=reply_to,
    #             subject=subject,
    #             mail_content=mail_content,
    #             template_name=template,
    #             recipient_list=recipient_list,
    #             cc_list=None,
    #             bcc_list=None,
    #             reply_to=reply_to,
    #             fail_silently=True)
    #
    #     except Exception as e:
    #         error_message = '{} : Contact - {}'.format(repr(e), contact_email)
    #         LOG.error(error_message)
    #         if settings.DEBUG:
    #             raise Exception(error_message)


class ComputeRequestProvisionSerializer(BaseProvisionMessageSerializer):
    """class ComputeRequestProvisionSerializer."""

    compute_product = PrimaryKeyLookupField(
        many=False, required=True, fields=[
            'id', 'name'], queryset=ComputeProduct.objects.all())

    def validate(self, data):
        """validate."""
        compute_product = data['compute_product']
        self.validate_user_provisions_product(
            AllocationComputeProductValidate.get_compute_product_obj(compute_product))
        try:
            # self.instance will force save action to perform update
            self.instance = ComputeRequest.objects.get(pk=data['id'])

            if not self.instance.provision_details:
                msg = '{} , request {} was never sent for provisioning'
                raise exceptions.ValidationError(
                    {'compute_request': msg.format(repr(self.instance), repr(self.instance.request))})

            if self.instance.provision_details.status not in \
                    ProvisionDetails.SET_OF_SENT:
                msg = '{} cannot be updated, status not in sent'
                raise exceptions.ValidationError({'compute_request': msg.format(repr(self.instance))})

            if self.instance.compute_product.id != compute_product['id']:
                msg = 'Invalid Product (id = {}) for {}'
                raise exceptions.ValidationError(
                    {'compute_request': msg.format(repr(compute_product['id']), repr(self.instance))})

            if 'success' not in data:
                raise exceptions.ValidationError({
                    'success': 'Field value is required'})

        except ComputeRequest.DoesNotExist:
            raise exceptions.ValidationError(
                {'compute_request': 'Compute Request not found for id {}'
                    .format(repr(data['id']))
                 })

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        """update."""
        provision_details = instance.provision_details
        success = validated_data['success']
        if success:
            provision_details.status = ProvisionDetails.PROVISIONED
        else:
            resend = validated_data.get('resend', False)
            if resend:
                provision_details.status = ProvisionDetails.RESEND_LATER
            else:
                provision_details.status = ProvisionDetails.FAILED

        provision_details.message = validated_data.get('message', None)

        provision_details.save()
        validated_data['update_success'] = True
        return validated_data


class StorageRequestProvisionSerializer(BaseProvisionMessageSerializer):
    OVERRIDE_PROVISION_ID = 'OVERRIDE_PROVISION_ID'
    """class StorageRequestProvisionSerializer."""

    storage_product = PrimaryKeyLookupField(
        many=False, required=True, fields=[
            'id', 'name'], queryset=StorageProduct.objects.all())

    provision_id = serializers.CharField(max_length=255, required=False)

    @classmethod
    def validate_get_provision_id_current_use(cls, validated_data, sr_instance):
        provision_id = validated_data.get('provision_id')
        if not provision_id:
            return
        return provision_utils.validate_current_use_return_provision_id(provision_id, sr_instance)

    def get_override_provision_id_flag(self):
        return self.context.get(self.OVERRIDE_PROVISION_ID, False)

    def validate(self, data):
        """validate."""
        storage_product_obj = data['storage_product']
        self.validate_user_provisions_product(storage_product_obj)
        try:
            # self.instance will force save action to perform update
            self.instance = StorageRequest.objects.get(pk=data['id'])
            if not self.instance.provision_details:
                msg = '{}  request {} was never sent for provisioning'
                raise exceptions.ValidationError(
                    {'storage_request': msg.format(repr(self.instance), repr(self.instance.request))})

            override_provision_process = self.get_override_provision_id_flag()
            if override_provision_process and \
                    self.instance.provision_details.status == ProvisionDetails.PROVISIONED:
                pass
            elif self.instance.provision_details.status not in \
                    ProvisionDetails.SET_OF_SENT:
                raise exceptions.ValidationError(
                    {'storage_request':
                        '{} {} cannot be updated, status not in sent'.format(
                            repr(self.instance),
                            self.instance.provision_details.status)})

            if self.instance.storage_product != storage_product_obj:
                msg = 'Invalid Product (id = {}) for {}'
                raise exceptions.ValidationError(
                    {'storage_request': msg.format(repr(storage_product_obj), repr(self.instance))})

            # do not set provision id here, it keeps looping with pid_obj text
            data['provision_id_obj'] = \
                self.validate_get_provision_id_current_use(data, self.instance)
            if 'success' not in data:
                raise exceptions.ValidationError({'success': 'Field value is required'})
        except StorageRequest.DoesNotExist:
            raise exceptions.ValidationError(
                {'storage_request': 'Storage Request not found for id {}'.format(repr(data['id']))})

        return data

    # @transaction.atomic
    def update(self, instance, validated_data):
        """update."""
        provision_details = instance.provision_details
        success = validated_data['success']
        message = validated_data.get('message', None)

        override_provision_process = self.get_override_provision_id_flag()
        if not override_provision_process:
            if success:
                provision_details.status = ProvisionDetails.PROVISIONED
            else:
                resend = validated_data.get('resend', False)
                if resend:
                    provision_details.status = ProvisionDetails.RESEND_LATER
                else:
                    provision_details.status = ProvisionDetails.FAILED

            provision_details.message = message
            provision_details.save()

        validated_data['update_success'] = True

        # update Provision Id
        provision_id_obj = validated_data.pop('provision_id_obj', None)
        if not instance.provision_id == provision_id_obj:
            prev_provision_id = instance.provision_id
            instance.provision_id = provision_id_obj
            instance.save()
            user_obj = self.get_current_user()
            ProvisionMetaLogger.log_provision_id_change(instance, prev_provision_id, user_obj)

        return validated_data


class UpdateProvisionRequestSerializer(BaseProvisionSerializer):
    """class UpdateProvisionRequestSerializer."""

    compute_requests = serializers.SerializerMethodField()

    storage_requests = serializers.SerializerMethodField()

    sent_email = serializers.BooleanField(default=True)

    @classmethod
    def get_crams_request_serializer_class(cls):
        return CramsRequestWithoutProjectSerializer

    @classmethod
    def get_compute_requests(cls, request_obj):
        return list()

    @classmethod
    def get_storage_requests(cls, request_obj):
        return list()

    def validate_product_request(self, in_product_request_data, product_type):
        ret_product_sz_list = list()
        err_dict = dict()
        req_count = 0

        if product_type == 'compute requests':
            product_type_instances = self.instance.compute_requests.all()
            product_type_sz_class = ComputeRequestProvisionSerializer
        elif product_type == 'storage_requests':
            product_type_instances = self.instance.storage_requests.all()
            product_type_sz_class = StorageRequestProvisionSerializer
        else:
            err_dict[req_count] = 'system error: unknown product type provided'
            raise exceptions.ValidationError(err_dict)

        for in_product_request in in_product_request_data:
            req_count += 1
            err_list = list()
            product_request_id = in_product_request.get('id')
            if not product_request_id:
                err_list.append('field "id" required, got ' + in_product_request)
            else:
                existing_product_request = next(
                    (x for x in product_type_instances
                     if x.id == product_request_id), None)
                if not existing_product_request:
                    msg = '{} Request with id {} does not belong to {}'
                    err_list.append(msg.format(product_type, repr(product_request_id), repr(self.instance)))
                else:
                    product_request_serializer = product_type_sz_class(
                        data=in_product_request, context=self.context)
                    product_request_serializer.is_valid(raise_exception=False)
                    if product_request_serializer.errors:
                        err_list = list(product_request_serializer.errors)
                    else:
                        ret_product_sz_list.append(product_request_serializer)
            if len(err_list) > 0:
                err_dict[req_count] = err_list

        if len(err_dict) > 0:
            raise exceptions.ValidationError({product_type: err_dict})

        return ret_product_sz_list

    def validate(self, data):
        """validate."""
        request_id = data.get('id', None)
        if not request_id:
            raise exceptions.ValidationError(
                {'request': 'field "id" required, got ' + data})

        try:
            current_user, _ = project_user_utils.get_current_user_from_context(self)
            if not AbstractCramsRoleUtils.is_user_a_provider(current_user):
                raise exceptions.ValidationError(
                    {'message': 'User is not a provider'})

            # self.instance will force save action to perform update
            self.instance = Request.objects.get(pk=request_id)
            if not self.instance:
                raise exceptions.ValidationError(
                    {'request': 'Request with id {} does not belong to {}'.format(repr(request_id), repr(self.instance))})
            if (self.instance.request_status.code not in
                    PROVISION_ENABLE_REQUEST_STATUS):
                msg = 'Request status is not Approved, provision update fail for {}'
                raise exceptions.ValidationError(
                    {'request': msg.format(repr(self.instance))})

            # validate product requests
            to_validate = ['compute_requests', 'storage_requests']
            for prod_req_type in to_validate:
                in_prod_requests = self.initial_data.get(prod_req_type, list())
                if in_prod_requests:
                    data[prod_req_type] = self.validate_product_request(
                        self.initial_data.get(prod_req_type), product_type=prod_req_type)

        except Request.DoesNotExist:
            raise exceptions.ValidationError({
                'message': 'Request not found for id {}'.format(
                    repr(request_id))})

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        """update."""
        # process compute request provisioning result
        for product_request_serializer in validated_data.pop('compute_requests', list()):
            product_request_serializer.save(request=instance)
        validated_data['compute_requests'] = list()

        # process storage request provisioning result
        for product_request_serializer in validated_data.pop('storage_requests', list()):
            product_request_serializer.save(request=instance)
        validated_data['storage_requests'] = list()

        # update the sent_email
        # instance.sent_email = validated_data["sent_email"]
        # instance.save()

        send_email_flag = validated_data["sent_email"]
        new_status_code = self._update_request_status(instance, send_email_flag)
        validated_data['new_request_status'] = new_status_code

        # if new_status_code == instance.request_status.code and send_email_flag:
        #     # no change to request status, implies partial provisioning
        #     notify_cls = allocation_notification.AllocationNotificationUtils
        #     notify_cls.send_partial_provision_notification(
        #         instance, self.context)
        #
        # # set a review record for request if available
        # set_review(instance)
        return validated_data

    def _update_request_status(self, instance, sent_email):

        if not instance:
            msg = 'update request status failed, no existing instance passed in UpdateProvisionRequestSerializer'
            raise exceptions.ValidationError(
                {'Severe Error, Contact Support': msg})

        status_code_to_update = REQUEST_STATUS_PROVISIONED
        for cpr in instance.compute_requests.all():
            if not (cpr.provision_details and cpr.provision_details.status ==
                    ProvisionDetails.PROVISIONED):
                status_code_to_update = None
                break

        if status_code_to_update:
            for spr in instance.storage_requests.all():
                if not (spr.provision_details and
                        spr.provision_details.status ==
                        ProvisionDetails.PROVISIONED):
                    status_code_to_update = None
                    break

        if status_code_to_update:
            context = dict()
            context['request'] = self.context['request']

            context[OVERRIDE_READONLY_DATA] = {
                'request_status': status_code_to_update,
                DO_NOT_OVERRIDE_PROVISION_DETAILS: True
            }

            # set the sent_email flag to the request
            self._set_sent_email_to_context(context, instance.id, sent_email)

            req_sz_class = self.get_crams_request_serializer_class()
            update_data = {"id": instance.id}

            new_request = req_sz_class(
                instance, data=update_data, partial=True, context=context)
            new_request.is_valid(raise_exception=True)
            new_request.save()
            return status_code_to_update

        return instance.request_status.code  # return existing status code

    @classmethod
    def _set_sent_email_to_context(cls, context, req_id, sent_email):
        requests = context['request'].data['requests']
        req_idx = next((idx for idx, val in enumerate(requests)
                        if val['id'] == req_id), None)

        if req_idx:
            context['request'].data['requests'][req_idx]['sent_email'] = sent_email


class UpdateProvisionProjectSerializer(BaseProvisionMessageSerializer):
    requests = serializers.SerializerMethodField()
    # project_ids = project_id_serializers.ProjectIDExImSerializer(
    #     many=True, required=False)

    @classmethod
    def get_class(cls):
        return cls

    def get_requests(self, in_project_data):
        project_obj = self.get_project(in_project_data.get('id'))
        if project_obj and hasattr(project_obj, 'requests'):
            request_qs = project_obj.requests.filter(current_request__isnull=True)
            if request_qs:
                sz_class = self.get_update_provision_request_serializer()
                return sz_class(request_qs, many=True, context=self.context).data
        return list()

    @classmethod
    def get_update_provision_request_serializer(cls):
        return UpdateProvisionRequestSerializer

    @classmethod
    def get_project(cls, pk):
        # msg = 'Project cannot be determined for pk {}'.format(pk)
        try:
            obj = Project.objects.get(pk=pk)
            if obj.current_project:
                obj = obj.current_project
            return obj
        except Project.DoesNotExist:
            msg = 'Project does not exist for pk {}'.format(pk)
        return exceptions.ValidationError(msg)

    # def validate_project_identifiers(self, data_including_project_pk):
    #     id_key = 'project_ids'
    #     sz_class = projectid_contact_provision.ProvisionProjectIDSerializer
    #     ret_list = sz_class.validate_project_identifiers_in_project_list(
    #         [data_including_project_pk], self.get_current_user(), id_key)
    #     return ret_list[0].get(id_key)

    def validate_requests(self):
        ret_sz_list = list()
        err_list = list()
        sz_class = self.get_update_provision_request_serializer()
        for product_request_data in self.initial_data.get('requests', list()):
            sz = sz_class(data=product_request_data, context=self.context)
            sz.is_valid(raise_exception=False)
            if sz.errors:
                err_list += list(sz.errors)
            else:
                ret_sz_list.append(sz)
        if err_list:
            raise exceptions.ValidationError(err_list)

        return ret_sz_list

    def validate(self, data):
        # set instance to invoke update instead of create
        self.instance = self.get_project(data.get('id'))

        # validate and prepare project identifiers for update
        ret_data = dict()
        ret_data['requests'] = self.validate_requests()
        # ret_data['project_ids'] = self.validate_project_identifiers(data)
        return ret_data

    @transaction.atomic
    def update(self, instance, validated_data):
        # # update project id provisioning
        # sz = projectid_contact_provision.ProvisionProjectIDSerializer
        # id_key = 'project_ids'
        # p_ids = sz.update_project_data_list(id_key, [validated_data])
        # if p_ids:
        #     pid_update_result = sz.build_project_id_list_json(p_ids)
        #     validated_data[id_key] = pid_update_result[0].get(id_key)

        # update request provisioning
        out_requests = list()
        for request_serializer in validated_data.pop('requests', list()):
            out_requests.append(request_serializer.save(project=instance))

        validated_data['requests'] = out_requests
        validated_data['id'] = instance.id
        validated_data['success'] = True
        return validated_data
