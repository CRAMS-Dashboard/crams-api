# coding=utf-8
"""
Mail Sender methods
"""
from collections import Iterable

from django.template import Context
from django.template.loader import get_template
from django.core.mail import EmailMessage

from django.conf import settings
import threading

__author__ = 'simonyu, rafi feroze, melvin luong'


class EmailThread(threading.Thread):
    def __init__(self, sender, subject, mail_content, recipient_list, template_name=None, cc_list=None, bcc_list=None,
                 reply_to=None, fail_silently=False):
        self.sender = sender
        self.subject = subject
        self.mail_content = mail_content
        self.recipient_list = recipient_list
        self.template_name = template_name
        self.cc_list = cc_list
        self.bcc_list = bcc_list
        self.reply_to = reply_to
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_email(sender=self.sender, subject=self.subject, mail_content=self.mail_content,
                   recipient_list=self.recipient_list, template_name=self.template_name, cc_list=self.cc_list,
                   bcc_list=self.bcc_list, reply_to=self.reply_to, fail_silently=self.fail_silently)


def filter_email_for_non_prod_environment(email_address_list):
    return email_address_list


def append_non_prod_env_to_subject(subject):
    if settings.CURRENT_RUN_ENVIRONMENT is not settings.PROD_ENVIRONMENT:
        # append env to subject
        return "[" + settings.CURRENT_RUN_ENVIRONMENT + "] " + subject

    return subject


def send_email(
        sender,
        subject,
        mail_content,
        recipient_list,
        template_name=None,
        cc_list=None,
        bcc_list=None,
        reply_to=None,
        fail_silently=False):
    """
    send notification
    :param sender:
    :param subject:
    :param mail_content:
    :param recipient_list:
    :param template_name:
    :param cc_list:
    :param bcc_list:
    :param reply_to:
    :param fail_silently: used for testing
    """
    if template_name:
        template = get_template(template_name)
        ctx = Context({'request': mail_content})
        message = template.render(ctx)
    else:
        message = mail_content

    sender_email = sender
    if not isinstance(sender, str):
        if isinstance(sender, Iterable):
            for s in sender:
                sender_email = s
                break

    subject = append_non_prod_env_to_subject(subject)

    to_list = filter_email_for_non_prod_environment(recipient_list)
    email = EmailMessage(subject=subject, body=message,
                         from_email=sender_email, to=to_list)
    if cc_list:
        email.cc = filter_email_for_non_prod_environment(cc_list)
    if bcc_list:
        email.bcc = filter_email_for_non_prod_environment(bcc_list)
    if reply_to:
        email.reply_to = filter_email_for_non_prod_environment(reply_to)

    email.send(fail_silently=fail_silently)


def send_notification(sender, subject, mail_content, recipient_list, template_name=None, cc_list=None, bcc_list=None,
                      reply_to=None, fail_silently=False):
    EmailThread(sender, subject, mail_content, recipient_list, template_name, cc_list, bcc_list, reply_to,
                fail_silently).start()
