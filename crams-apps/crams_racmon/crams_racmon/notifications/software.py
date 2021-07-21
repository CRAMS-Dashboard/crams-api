from crams_allocation.models import NotificationContactRole
from crams_allocation.models import NotificationTemplate
from crams_notification.tasks import mail_sender
from crams_notification.utils import mail_util
from crams_racmon.config import config_init as conf
from crams.models import SoftwareLicenseStatus


def send_software_notification(contact_software_license):
    erb = contact_software_license.license.software.e_research_body
    status = SoftwareLicenseStatus.objects.get(
        code=contact_software_license.status)

    # get the notification template
    try:
        notification_temp = NotificationTemplate.objects.get(
            contact_license_status=status, e_research_body=erb)
    except:
        # if no template exist fail siliently
        return

    # get the contact role/s who should receive the email
    notification_roles = NotificationContactRole.objects.filter(
        notification=notification_temp)

    email_list = []

    # if contact role is 'Applicant'
    #     get the contact from the contact license
    applicant = notification_roles.filter(
        contact_role__name__icontains='applicant')
    if applicant.first():
        email_list.append(contact_software_license.contact.email)

    # if contact role is 'E_RESEARCH_BODY Admin' get all erb admins
    # from EResearchContact
    admin = notification_roles.filter(
        contact_role__name__icontains='e_research_body admin')
    if admin.first():
        # append each admin email to email_list as a recipient
        for er_contact in erb.contacts.filter(end_date_ts__isnull=True):
            email_list.append(er_contact.contact.email)

    subject = ("Software License request: " +
               contact_software_license.license.software.name)

    # append Approved or Decline at the end
    if status.code != 'R':
        subject = subject + " - " + status.status

    contact_software_license_dict = {
        "contact": {
            "given_name": contact_software_license.contact.given_name,
            "surname": contact_software_license.contact.surname,
            "email": contact_software_license.contact.email
        },
        "license": {
            "software": {
                "name": contact_software_license.license.software.name,
            },
            "type": {
                "type": contact_software_license.license.type.type
            }
        }
    }

    content = {"software_license": contact_software_license_dict}
    
    reply_to = conf.RDSM_REPLY_TO_EMAIL
    sender = conf.RDSM_SENDER_EMAIL

    # send email
    mail_content = mail_util.render_mail_content(
        notification_temp.template_file_path, content)
    mail_sender.send_email(sender=sender,
                           subject=subject,
                           mail_content=mail_content,
                           recipient_list=list(set(email_list)),
                           cc_list=None,
                           bcc_list=None,
                           fail_silently=False,
                           reply_to=reply_to)