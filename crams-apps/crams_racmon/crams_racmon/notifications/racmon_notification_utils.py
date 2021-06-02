# coding=utf-8
"""racmon allocation notification """

import logging

from crams.constants.db import E_RESEARCH_BODY_ADMIN, E_RESEARCH_BODY_SYSTEM_ADMIN
from crams.constants.db import E_RESEARCH_BODY_SYSTEM_APPROVER
from crams.constants.db import E_RESEARCH_BODY_SYSTEM_PROVISIONER, APPLICANT
from crams.models import Provider
from crams_allocation.constants.db import REQUEST_STATUS_APPROVED, REQUEST_STATUS_PARTIAL_PROVISIONED
from crams_allocation.models import NotificationTemplate
from crams_allocation.serializers.project_request_serializers import ReadOnlyCramsRequestWithoutProjectSerializer
from crams_collection.serializers.base_project_serializer import ReadOnlyProjectSerializer
from crams_notification.tasks import mail_sender
from crams_notification.utils import mail_util
from django.conf import settings
from django.db.models import Q
import json

LOG = logging.getLogger(__name__)


class RacmonAllocationNotificationUtils:
    @classmethod
    def populate_email_dict_for_request(cls, alloc_request, serializer_context):
        """

        :param alloc_request:
        :param serializer_context:
        :return:
        """
        serializer = ReadOnlyCramsRequestWithoutProjectSerializer(alloc_request, context=serializer_context)
        ret_dict = serializer.data

        project_serializer = ReadOnlyProjectSerializer(alloc_request.project, many=False, context=serializer_context)
        ret_dict['project'] = project_serializer.data

        request_url = settings.RACMON_CLIENT_BASE_URL + settings.RACMON_CLIENT_VIEW_REQUEST_PATH
        ret_dict['client_request_url'] = request_url + str(alloc_request.id)

        approval_url = settings.RACMON_CLIENT_BASE_URL + settings.RACMON_CLIENT_VIEW_APPROVAL_PATH
        ret_dict['client_approval_url'] = approval_url + str(alloc_request.id)

        return ret_dict

    @classmethod
    def fetch_and_process_notification_template(cls, alloc_req, base_filter, serializer_context):
        or_filter = Q()
        if alloc_req.e_research_system:
            or_filter |= Q(e_research_system=alloc_req.e_research_system)
        if alloc_req.funding_scheme:
            fb = alloc_req.funding_scheme.funding_body
            or_filter |= Q(funding_body=fb)
        if or_filter:
            base_filter &= or_filter
        for n_template in NotificationTemplate.objects.filter(base_filter):
            cls.process_notification_template(
                n_template, alloc_req, serializer_context)

    @classmethod
    def send_notification(cls, alloc_req, serializer_context):
        """

        :param alloc_req:
        :param serializer_context:
        :return:
        """
        if alloc_req.sent_email:
            base_filter = Q(request_status=alloc_req.request_status)
            cls.fetch_and_process_notification_template(alloc_req, base_filter, serializer_context)

    @classmethod
    def send_partial_provision_notification(cls, alloc_req, serializer_context):
        """

        :param alloc_req:
        :param serializer_context:
        :return:
        """
        req_status_code = alloc_req.request_status.code
        msg = 'partial provision email invoked for request with status {}: {}'
        if not req_status_code == REQUEST_STATUS_APPROVED:
            # Request status must be in approved state for partial provisioned
            LOG.error(msg.format(alloc_req, req_status_code))
            return

        partial_provision_status_code = REQUEST_STATUS_PARTIAL_PROVISIONED
        base_filter = Q(request_status__code=partial_provision_status_code)
        cls.fetch_and_process_notification_template(alloc_req, base_filter, serializer_context)

    @classmethod
    def process_notification_template(
            cls, template_obj, alloc_req, serializer_context):
        """

        :param template_obj:
        :param alloc_req:
        :param serializer_context:
        :return:
        """
        template = template_obj.template_file_path

        mail_content = cls.populate_email_dict_for_request(alloc_req, serializer_context)
        desc = alloc_req.project.title
        subject = 'Allocation request - ' + desc

        try:
            recipient_list = cls.get_request_notification_recipient_list(alloc_req, template_obj)

            if template_obj.alert_funding_body:
                if alloc_req.funding_scheme:
                    fb_obj = alloc_req.funding_scheme.funding_body
                    if fb_obj.email:
                        recipient_list.append(fb_obj.email)
                else:
                    p_msg = 'FB not found for request, Unable to alert FB'
                    LOG.warning(p_msg)

            reply_to = list()
            if alloc_req.e_research_system:
                reply_to = None  # TODO to decide where this comes from
            json_string = json.dumps(mail_content)
            print('======> mail content json: {}'.format(json_string))
            mail_message = mail_util.render_mail_content(template, mail_content)
            mail_sender.send_email(
                sender=reply_to,
                subject=subject,
                mail_content=mail_message,
                recipient_list=recipient_list,
                cc_list=None,
                bcc_list=None,
                reply_to=reply_to)

        except Exception as e:
            error_message = '{} : Project - {}'.format(repr(e), desc)
            LOG.error(error_message)
            if settings.DEBUG:
                raise Exception(error_message)

    @classmethod
    def get_request_notification_recipient_list(cls, alloc_req, template_obj):
        """

        :param alloc_req:
        :param template_obj:
        :return:
        """
        recipient_list = list()
        e_research_system = alloc_req.e_research_system
        if not e_research_system:
            msg = 'Request is not associated with e_research_body_system'
            LOG.error(msg)
            LOG.error(alloc_req)
            return

        for notify_role in template_obj.notify_roles.all():
            role_name = notify_role.contact_role.name
            if role_name == E_RESEARCH_BODY_ADMIN:
                erb_obj = e_research_system.e_research_body
                for erb_admin in erb_obj.contacts.filter(is_erb_admin=True):
                    recipient_list.append(erb_admin.contact.email)
            elif role_name == E_RESEARCH_BODY_SYSTEM_ADMIN:
                for erbs_contact in e_research_system.admin_contacts.all():
                    recipient_list.append(erbs_contact.contact.email)

            elif role_name == E_RESEARCH_BODY_SYSTEM_APPROVER:
                for erbs_contact in e_research_system.approver_contacts.all():
                    recipient_list.append(erbs_contact.contact.email)

            elif role_name == E_RESEARCH_BODY_SYSTEM_PROVISIONER:
                for provider in Provider.objects.filter(
                        storageproduct__storage_requests__request=alloc_req):
                    for provider_contact in provider.provider_contacts.all():
                        recipient_list.append(provider_contact.contact.email)

            elif role_name == APPLICANT:
                recipient_list.append(alloc_req.project.created_by.email)
            else:
                for pc in alloc_req.project.project_contacts.filter(
                        contact_role=notify_role.contact_role):
                    recipient_list.append(pc.contact.email)

        # remove duplicate emails from recipient list
        # NB: (approvers/provisioners/applicants can be the same person)
        return list(set(recipient_list))
