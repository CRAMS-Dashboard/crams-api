import logging
from crams.models import EResearchBodyDelegate
from crams.models import Question
from crams_allocation.config.allocation_config import DELEGATE_QUESTION_KEY_MAP
from crams_allocation.models import NotificationContactRole
from crams_allocation.models import NotificationTemplate
from crams_allocation.models import RequestQuestionResponse
from crams_collection.models import ProjectContact
from crams_collection.models import ProjectID
from crams_contact.models import CramsERBUserRoles
from crams_notification.tasks import mail_sender
from crams_notification.utils import mail_util
from crams_racmon.config import config_init as conf

logger = logging.getLogger(__name__)

def send_membership_notification(subject, prj_join_invite_request,
                                 member_status_code, erbs, prj_lead_contacts=[],
                                 additional_params=None):
    project = prj_join_invite_request.project
    
    # try and get project_system_id
    project_system_id = None
    try:
        project_system_id = ProjectID.objects.get(
            project=project).identifier
    
        project_full_title = project_system_id + " - " + project.title
    except:
        project_full_title = project.title
    
    # email subject
    subject = subject + project_full_title
    
    # invitee name - first name + last name
    # if unable to retrieve the fullname, display their email
    try:
        invitee_name = (prj_join_invite_request.given_name + ' ' +
                        prj_join_invite_request.surname)
    except:
        invitee_name = prj_join_invite_request.email
    
    # set name
    # if more than 1 project leader in group remains then the name is NULL
    # will be up to the template to set a plural name
    # i.e Project Leaders, Chief Investigators..
    prj_lead_name = None
    if len(prj_lead_contacts) == 1:
        try:
            prj_lead_name = (prj_lead_contacts[0].given_name +
                                ' ' + prj_lead_contacts[0].surname)
            # append title to ci if exist
            if prj_lead_contacts[0].title:
                prj_lead_name = (prj_lead_contacts[0].title +
                                    ' ' + prj_lead_name)
        except:
            prj_lead_name = prj_lead_contacts[0].email
    
    # append the request id
    req = project.requests.all().filter(current_request=None).first()
    request_url = conf.REQUEST_URL
    if req:
        request_url += str(req.id)
    
    # member url
    member_url = conf.MEMBER_URL + str(project.id)
    
    # hpc user posix id
    # try:
    #     erb_id_key = EResearchBodyIDKey.objects.get(key='HPC_POSIX_USERID')
    #     erb_contact_id = EResearchContactIdentifier.objects.get(
    #         contact__email=prj_join_invite_request.email, system_id=erb_id_key)
    #     hpc_user_posix_id = erb_contact_id.identifier
    # except:
    #     hpc_user_posix_id = None
    
    # get all the templates
    notification_temps = NotificationTemplate.objects.filter(
        e_research_system=erbs,
        project_member_status__code=member_status_code)
    
    # sends out all the notification emails for membership status
    for notification_temp in notification_temps:
        template = notification_temp.template_file_path
    
        # get the notification contacts,
        # any additional recipients of the email
        email_contact_roles = NotificationContactRole.objects.filter(
            notification=notification_temp)
    
        content = {"invitee_name": invitee_name,
                   "invitee_email": prj_join_invite_request.email,
                   "invitee_fname": prj_join_invite_request.given_name,
                   "invitee_lname": prj_join_invite_request.surname,
                   "prj_lead_name": prj_lead_name,
                   "base_url": conf.BASE_URL,
                   "request_url": request_url,
                   "join_url": conf.JOIN_URL,
                   "member_url": member_url,
                   "project_full_title": project_full_title
                   # "user_id": hpc_user_posix_id,
                   # "project_id": project_system_id
                   }
    
        # add any additional dict to mail_content
        if additional_params:
            content.update(additional_params)
    
        # compile the list of recipients to email
        recipient_list = get_recipient_list(
            prj_jn_inv_req=prj_join_invite_request,
            email_contact_roles=email_contact_roles,
            erbs=erbs)
    
        reply_to = conf.RDSM_REPLY_TO_EMAIL
    
        # send email invitation to user
        try:
            mail_content = mail_util.render_mail_content(template, content)
            mail_sender.send_email(sender=reply_to,
                                   subject=subject,
                                   mail_content=mail_content,
                                   recipient_list=recipient_list,
                                   cc_list=None,
                                   bcc_list=None,
                                   fail_silently=False)
        except Exception as ex:
            logger.error('Error sending email notification: ' + str(ex))


# get recipient list
def get_recipient_list(prj_jn_inv_req,
                       email_contact_roles, erbs):
    recipient_list = []

    # Get all the contact roles that whom will receive an email
    contact_roles = []
    for ecr in email_contact_roles:
        contact_roles.append(ecr.contact_role.name)

    # invitee is the user that has been invited or has requested
    # to join the project
    if conf.INVITEE in contact_roles:
        recipient_list.append(prj_jn_inv_req.email)

    # add regular project contact emails
    if contact_roles:
        prj_contacts = ProjectContact.objects.filter(
            contact_role__name__in=contact_roles,
            project=prj_jn_inv_req.project)
        for prj_cont in prj_contacts:
            recipient_list.append(prj_cont.contact.email)

    # add erb admin contact emails
    if conf.E_RESEARCH_BODY_ADMIN in contact_roles:
        erb_admin_contacts = CramsERBUserRoles.objects.filter(
            role_erb=erbs.e_research_body, is_erb_admin=True)
        for admin_contact in erb_admin_contacts:
            recipient_list.append(admin_contact.contact.email)

    # add erbs admin contact emails
    if conf.E_RESEARCH_BODY_SYSTEM_ADMIN in contact_roles:
        erbs_admin_contacts = CramsERBUserRoles.objects.all()
        for erbs_admin_contact in erbs_admin_contacts:
            for erb_system in erbs_admin_contact.admin_erb_systems.all():
                if erb_system == erbs:
                    recipient_list.append(erbs_admin_contact.contact.email)
                    break

    # add erbs approver contact emails
    if conf.E_RESEARCH_BODY_SYSTEM_APPROVER in contact_roles:
        erbs_approver_contacts = CramsERBUserRoles.objects.all()
        for erbs_approver_contact in erbs_approver_contacts:
            for erb_system in erbs_approver_contact.approver_erb_systems.all():
                if erb_system == erbs:
                    recipient_list.append(erbs_approver_contact.contact.email)
                    break

    # add providers(provisioner) contact emails
    if conf.E_RESEARCH_BODY_SYSTEM_PROVISIONER in contact_roles:
        provider_contacts = CramsERBUserRoles.objects.filter(
            role_erb=erbs.e_research_body,
            providers__isnull=False).distinct()

        for prv_contact in provider_contacts:
            recipient_list.append(prv_contact.contact.email)

    # add delegates contact emails
    if conf.E_RESEARCH_SYSTEM_DELEGATE in contact_roles:
        # get the project share if available
        delegate = get_delegate(prj_jn_inv_req.project)
        delegate_contacts = CramsERBUserRoles.objects.all()
        for delegate_contact in delegate_contacts:
            for delg in delegate_contact.delegates.all():
                if delg == delegate:
                    recipient_list.append(delegate_contact.contact.email)
                    break

    # remove duplicate emails in the recipient list
    recipient_list = list(set(recipient_list))

    return recipient_list


def get_delegate(project):
    # get request_obj
    request_obj = project.requests.first()

    # get question_key for delegate
    del_key = DELEGATE_QUESTION_KEY_MAP.get(
        request_obj.e_research_system.name)

    if del_key:
        q = Question.objects.get(key=del_key)
        rq = RequestQuestionResponse.objects.filter(
            question=q, request=request_obj)

        if rq.exist():
            del_name = rq.first().question_response
            try:
                return EResearchBodyDelegate.objects.get(
                    name__iexact=del_name)
            except:
                return None

    return None
