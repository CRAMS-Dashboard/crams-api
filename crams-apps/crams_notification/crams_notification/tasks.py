from celery import task
from .mail import mail_sender
from django.conf import settings


@task()
def send_email_notification(sender, subject, mail_content, recipient_list, cc_list=None, bcc_list=None,
                            reply_to=None, fail_silently=False):
    mail_sender.send_email(sender, subject, mail_content, recipient_list, cc_list, bcc_list,
                           reply_to, fail_silently)


def send_email(sender, subject, mail_content, recipient_list, cc_list=None, bcc_list=None,
               reply_to=None, fail_silently=False):
    if settings.MQ_MAIL_ENABLED:
        send_email_notification.delay(sender, subject, mail_content, recipient_list, cc_list=None, bcc_list=None,
                                      reply_to=None, fail_silently=False)
    else:
        mail_sender.EmailThread(sender, subject, mail_content, recipient_list, cc_list, bcc_list,
                                reply_to, fail_silently).start()
