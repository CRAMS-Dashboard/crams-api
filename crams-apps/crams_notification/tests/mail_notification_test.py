from crams.test_utils import CommonBaseTestCase

from django.conf import settings
from django.core import mail

from crams_notification.mail import mail_sender
from crams_notification.utils import mail_util


class TestMailNotification(CommonBaseTestCase):

    def setUp(self):
        self.sender = 'test@mcrams.com'
        self.subject = 'This is test mail'
        self.mail_content = 'Plain text message'
        self.recipient_list = ['test1@crams.com', 'test2@crams.com']
        self.cc_list = ['test3@crams.com', 'test4@crams.com']
        self.bcc_list = ['test5@crams.com', 'test6@crams.com']

    def test_mail_sender_plain_text(self):

        mail_sender.send_email(sender=self.sender, subject=self.subject, mail_content=self.mail_content,
                               recipient_list=self.recipient_list, cc_list=self.cc_list, bcc_list=self.bcc_list)
        assert len(mail.outbox) == 1
        message = mail.outbox[0]
        assert message.from_email == self.sender
        assert message.to == self.recipient_list
        assert message.cc == self.cc_list
        assert message.bcc == self.bcc_list

        if settings.CURRENT_RUN_ENVIRONMENT is not settings.PROD_ENVIRONMENT:
            # append env to subject
            assert message.subject == "[" + settings.CURRENT_RUN_ENVIRONMENT + "] " + self.subject
        else:
            assert message.subject == self.subject
        assert message.body == self.mail_content

    def test_mail_sender_with_template(self):
        self.mail_content = {
            'project': {
                'title': 'This is test project',
                'contact': 'test@crams.com'
            }
        }
        message = mail_util.render_mail_content('test_tpl/submit.tpl', mail_content_json=self.mail_content)
        assert message != None
        mail_sender.send_email(sender=self.sender, subject=self.subject, mail_content=message,
                               recipient_list=self.recipient_list, cc_list=self.cc_list, bcc_list=self.bcc_list)

        assert len(mail.outbox) == 1
        message = mail.outbox[0]
        assert message.from_email == self.sender
        assert message.to == self.recipient_list
        assert message.cc == self.cc_list
