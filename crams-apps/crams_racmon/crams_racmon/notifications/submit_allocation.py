# coding=utf-8
"""

"""
from django.db.models import Q
from django.conf import settings

from crams.utils import date_utils
from crams.models import EResearchBodyIDKey
from crams_notification.tasks import mail_sender
from crams_notification.utils import mail_util

from crams_racmon.config.config_init import racmon_support_email_dict, RDSM_REPLY_TO_EMAIL
from crams_collection.serializers.project_contact_serializer import ProjectContactSerializer

from crams_allocation.models import NotificationTemplate
from crams_allocation.config.allocation_config import ADMIN_ALERT_DATA_SENSITIVE
from crams_allocation.config.allocation_config import ADMIN_ALERT_QUESTION_KEYS
from crams_racmon.notifications.racmon_notification_utils import RacmonAllocationNotificationUtils


def submit_allocation_emails(existing_request_instance, request, serializer_context, is_clone_action=False):
    # # send admin email if any question changes that require an admin alert
    send_admin_email_alert(existing_request_instance, request)

    # send support email to an external ticketing system
    send_support_email(request)

    if not is_clone_action:
        RacmonAllocationNotificationUtils.send_notification(request, serializer_context=serializer_context)

    return True


def setup_rdsm_support_email_content(request_obj):
    request_url = settings.RACMON_CLIENT_BASE_URL + settings.RACMON_CLIENT_VIEW_REQUEST_PATH
    prj_cont_sz = ProjectContactSerializer(request_obj.project.project_contacts, many=True).data
    mail_content = dict()
    mail_content['updated_by'] = request_obj.updated_by.email
    mail_content['prj_title'] = request_obj.project.title
    mail_content['project_contacts'] = prj_cont_sz
    mail_content['url'] = request_url
    mail_content['prj_id'] = str(request_obj.project.id)
    mail_content['req_id'] = str(request_obj.id)

    return mail_content


# sends an email to an external ticketing system if erb has it configured
def send_support_email(request):
    # get erb and support email key
    erb = request.e_research_system.e_research_body

    # TODO : move the key and email to some db table
    key = racmon_support_email_dict.get('key')
    support_email = racmon_support_email_dict.get('email')

    sys_key = EResearchBodyIDKey.objects.filter(
        key=key, e_research_body=erb)

    # sys_key exist check grab all related templates
    if sys_key.first():
        temp_list = NotificationTemplate.objects.filter(
            Q(system_key=sys_key.first(), request_status=request.request_status))

        # check if this is not an edited request using the external
        # support email flag to avoid sending multiple emails
        if not request.sent_ext_support_email:
            for temp in temp_list:
                mail_content = setup_rdsm_support_email_content(request)
                # get the user who updated the req as the sender and reply_to
                reply_to = request.updated_by.email
                # fill out email attributes
                prj_title = request.project.title
                subject = 'Application {} - {}'.format(
                    request.request_status.status, prj_title)

                recipient_list = [support_email]
                template = temp.template_file_path
                mail_message = mail_util.render_mail_content(template, mail_content)
                mail_sender.send_email(
                    sender=reply_to,
                    subject=subject,
                    mail_content=mail_message,
                    recipient_list=recipient_list,
                    cc_list=None,
                    bcc_list=None
                )
                # set the ent_ext_support_email flag to true
                request.sent_ext_support_email = True
                request.save()


# Detects any question changes in the allocation that would require
# an email notification alert to be sent to the erb admin
def send_admin_email_alert(existing_req, new_request):
    ds_alert = dict()
    # stores list of question that have changed and trigger an alert
    q_alert = list()
    # skip if no previous existing project - this is a new application
    if not existing_req:
        return

    if not new_request.request_question_responses.exists():
        return

    # get erb object and name in lower case
    erb = existing_req.e_research_system.e_research_body
    erb_str = erb.name.lower()

    # get email template from erb, if no template exist skip this process
    notification_temp = NotificationTemplate.objects.filter(
        e_research_body=erb,
        system_key__key='ADMIN_ALERT_EMAIL').first()

    # if no email template found, with nothing to send exit function here
    if not notification_temp:
        return

    # get the data sensitive request flag
    new_response_dict = dict()
    for q_response in new_request.request_question_responses.all():
        new_response_dict[q_response.question] = q_response.question_response

    existing_response_dict = dict()
    if existing_req:
        for q_response in existing_req.request_question_responses.all():
            existing_response_dict[q_response.question] = q_response.question_response

    if erb_str in ADMIN_ALERT_DATA_SENSITIVE:
        # check if data sensitive has changed
        if not new_request.data_sensitive == existing_req.data_sensitive:
            # trigger email
            ds_alert = {'new_resp': new_request.data_sensitive,
                        'old_resp': existing_req.data_sensitive}

    # get the question keys that require an alert to be sent to admin
    q_key_list = []
    for q_key in ADMIN_ALERT_QUESTION_KEYS:
        for key, value in q_key.items():
            if erb_str == key:
                if value not in q_key_list:
                    q_key_list.append(value)

    if q_key_list:
        # request questions
        for question, new_response in new_response_dict.items():
            if question.key in q_key_list:
                # compare question with existing_req and has changed
                old_response = existing_response_dict.get(question, None)
                if not old_response == new_response:
                    # trigger email
                    q_alert.append(
                        {'question': question.question,
                         'new_resp': new_response,
                         'old_resp': old_response})

    # send email
    if ds_alert or q_alert:
        reply_to = RDSM_REPLY_TO_EMAIL
        prj_title = new_request.project.title
        subject = 'Application Updated - ' + prj_title

        # list of email content attribute
        mail_content = dict()
        # ds_alert
        mail_content['ds_alert'] = ds_alert
        # q_alert
        mail_content['q_alert'] = q_alert
        # updated by user
        mail_content['user_email'] = new_request.updated_by.email
        # date when updated
        mail_content['date_updated'] = date_utils.get_current_time_for_app_tz()
        # project title
        mail_content['prj_title'] = prj_title

        template = notification_temp.template_file_path
        notif_util = RacmonAllocationNotificationUtils
        recipient_list = notif_util.get_request_notification_recipient_list(
            existing_req, notification_temp)

        mail_message = mail_util.render_mail_content(template, mail_content)
        mail_sender.send_email(
            sender=reply_to,
            subject=subject,
            mail_content=mail_message,
            recipient_list=recipient_list,
            cc_list=None,
            bcc_list=None,
            reply_to=reply_to)
