import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from crams.models import EResearchBody
from crams.models import EResearchBodySystem
from crams.models import EResearchBodyIDKey
from crams.models import FundingBody
from crams_allocation.models import RequestStatus
from crams_contact.models import ContactRole
from crams_allocation.models import NotificationTemplate
from crams_allocation.models import NotificationContactRole


class TestNotificationModels(TestCase):
    def setUp(self):
        self.erb = mixer.blend(EResearchBody, name='erb')
        self.erbs = mixer.blend(EResearchBodySystem, name='erbs', e_research_body=self.erb)
        self.erb_id = mixer.blend(EResearchBodyIDKey, type='I', key="key", e_research_body=self.erb)
        self.funding_body = mixer.blend(FundingBody, name='Funding Body')
        self.req_status = RequestStatus.objects.get(code='P')
        self.submit_status = RequestStatus.objects.get(code='E')
        self.contact_role = mixer.blend(ContactRole, name="contact_role", e_research_body=self.erb)
        self.notification = mixer.blend(NotificationTemplate,
                                        funding_body = self.funding_body,
                                        system_key = self.erb_id,
                                        template_file_path = 'sample/submit.html',
                                        alert_funding_body = False,
                                        e_research_system = self.erbs,
                                        e_research_body = self.erb,
                                        request_status = self.req_status)

    def test_notification_template(self):
        notification_temp = NotificationTemplate()
        notification_temp.funding_body = self.funding_body
        notification_temp.system_key = self.erb_id
        notification_temp.template_file_path = 'sample/submit.html'
        notification_temp.alert_funding_body = False
        notification_temp.e_research_system = self.erbs
        notification_temp.e_research_body = self.erb
        notification_temp.request_status = self.submit_status
        notification_temp.save()
        
        # fetch saved obj
        try:
            saved_nt = NotificationTemplate.objects.get(pk=notification_temp.id)
        except:
            saved_nt = None

        # check saved values
        assert saved_nt
        assert saved_nt.funding_body == self.funding_body
        assert saved_nt.system_key == self.erb_id
        assert saved_nt.template_file_path == 'sample/submit.html'
        assert saved_nt.alert_funding_body == False
        assert saved_nt.e_research_system == self.erbs
        assert saved_nt.e_research_body == self.erb
        assert saved_nt.request_status == self.submit_status

    def test_notification_contact_role(self):
        notification_contact_role = NotificationContactRole()
        notification_contact_role.notification = self.notification
        notification_contact_role.contact_role = self.contact_role
        notification_contact_role.save()

        # fetch saved obj
        try:
            saved_ncr = NotificationContactRole.objects.get(pk=notification_contact_role.id)
        except:
            saved_ncr = None

        # check saved values
        assert saved_ncr
        assert saved_ncr.notification == self.notification
        assert saved_ncr.contact_role == self.contact_role