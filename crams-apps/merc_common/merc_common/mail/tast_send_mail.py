from celery import task

from crams.mail import mail_sender


@task(name="send_notification")
def send_email_notification(
        sender,
        subject,
        mail_content,
        recipient_list,
        template_name=None,
        cc_list=None,
        bcc_list=None,
        reply_to=None,
        fail_silently=False):
    mail_sender.send_email(sender, subject, mail_content, recipient_list, template_name, cc_list, bcc_list, reply_to,
                           fail_silently)
