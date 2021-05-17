import threading
from collections import Iterable

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template


class EmailThread(threading.Thread):
    def __init__(self, sender, subject, mail_content, recipient_list, cc_list=None, bcc_list=None,
                 reply_to=None, fail_silently=False):
        self.sender = sender
        self.subject = subject
        self.mail_content = mail_content
        self.recipient_list = recipient_list
        self.cc_list = cc_list
        self.bcc_list = bcc_list
        self.reply_to = reply_to
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_email(sender=self.sender, subject=self.subject, mail_content=self.mail_content,
                   recipient_list=self.recipient_list, cc_list=self.cc_list, bcc_list=self.bcc_list,
                   reply_to=self.reply_to, fail_silently=self.fail_silently)


def send_email(sender, subject, mail_content, recipient_list, cc_list=None, bcc_list=None, reply_to=None,
               fail_silently=False):
    """
    send notification
    :param sender:
    :param subject:
    :param mail_content:
    :param recipient_list:
    :param cc_list:
    :param bcc_list:
    :param reply_to:
    :param fail_silently: used for testing
    """

    sender_email = sender
    if not isinstance(sender, str):
        if isinstance(sender, Iterable):
            for s in sender:
                sender_email = s
                break

    subject = append_non_prod_env_to_subject(subject)

    to_list = recipient_list
    email = EmailMessage(subject=subject, body=mail_content, from_email=sender_email, to=to_list)
    if cc_list:
        email.cc = cc_list
    if bcc_list:
        email.bcc = bcc_list
    if reply_to:
        email.reply_to = reply_to

    email.send(fail_silently=fail_silently)


def append_non_prod_env_to_subject(subject):
    if settings.CURRENT_RUN_ENVIRONMENT is not settings.PROD_ENVIRONMENT:
        # append env to subject
        return "[" + settings.CURRENT_RUN_ENVIRONMENT + "] " + subject

    return subject
