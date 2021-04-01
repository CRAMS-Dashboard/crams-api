# coding=utf-8
"""
Email Tests
"""

from django.core import mail
from django.test import TestCase
# from crams.account.models import User

# from crams.models import Project, Request, RequestStatus
from merc_common.mail import mail_sender

import datetime


class EmailTest(TestCase):
    def setUp(self):
        self.request = {
            'request_data': 'To be filled'
        }
        # self.request = Request()
        # request_statue = RequestStatus()
        # request_statue.code = 'N'
        # self.request.request_status = request_statue
        # self.request.creation_date = datetime.date.today
        # self.request.last_modified = datetime.date.today
        # self.request.start_date = datetime.date.today
        # self.request.end_date = datetime.date.today

        # project = Project()
        # project.description = 'This is a mail testing'
        # created_by = User()
        # created_by.email = 'dummy@monash.edu'
        # updated_by = User()
        # updated_by.email = 'dummy@monash.edu'
        # self.request.project = project
        # self.request.created_by = created_by
        # self.request.updated_by = updated_by

    def test_email_send(self):
        sender = 'no-reply@tests.com'
        subject = "Allocation request - This is a mail testing"
        tpl_name = 'mail_tpl/notification.html'
        funding_body_email = "tests@monash.edu"
        recipient_list = [funding_body_email]
        mail_sender.send_notification(
            sender=sender,
            subject=subject,
            mail_content=self.request,
            template_name=tpl_name,
            recipient_list=recipient_list,
            cc_list=None,
            bcc_list=None,
            reply_to=None)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        self.assertEqual(subject, email.subject)
        for addr in recipient_list:
            self.assertIn(addr, email.to)
