from crams_demo.config import config_init as conf
from crams_notification.tasks import mail_sender
from crams_notification.utils import mail_util


def send_review_email_notification(subject, mail_content, template, recipient_list, cc_list):
    sender = conf.RDSM_SENDER_EMAIL
    reply_to = conf.RDSM_REPLY_TO_EMAIL

    mail_message = mail_util.render_mail_content(template, mail_content)
    mail_sender.send_email(
        sender=sender,
        subject=subject,
        mail_content=mail_message,
        recipient_list=recipient_list,
        cc_list=cc_list,
        bcc_list=None,
        reply_to=reply_to,
        fail_silently=False)

