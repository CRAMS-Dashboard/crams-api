import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from crams_log.models import LogType
from crams_log.models import LogAction
from crams_log.models import CramsLog
from crams_log.models import UserLog
from crams_log.serializers.cram_log_sz import CramsLogReadOnlySerializer
from crams_log.serializers.event_log import EventLogSerializer


class TestLogSerializers(TestCase):
    def setUp(self):
        self.log_type = mixer.blend(LogType, log_type='log_type', name='name', description='description')
        self.log_action = mixer.blend(LogAction, action_type='action_type', name='name', description='description')
        # needs to be saved as a string not json
        self.before_json_data = "{'project_title': 'Project Title1'}"
        self.after_json_data = "{'project_title': 'Project Title2'}"
        self.crams_log = mixer.blend(CramsLog,
            message = 'hello world',
            before_json_data = self.before_json_data,
            after_json_data = self.after_json_data,
            action = self.log_action,
            type = self.log_type,
            created_by = "test@test.com")

    def test_crams_log_readonly_sz(self):
        sz = CramsLogReadOnlySerializer(instance=self.crams_log)
        assert sz.data['message'] == self.crams_log.message
        assert sz.data['action'] == {'action_type': self.log_action.action_type, 'name': self.log_action.name}
        assert sz.data['type'] == {'log_type': self.log_type.log_type, 'name': self.log_type.name}
        assert sz.data['created_by'] == self.crams_log.created_by

    def test_event_log_sz(self):
        sz = EventLogSerializer(instance=self.crams_log)
        assert sz.data['project_title'] == 'TODO project title fetch'
        assert sz.data['event'] == self.crams_log.message + ' - ' + self.crams_log.action.name
        changes = sz.data['changes'][0]
        assert changes['type'] == 'change'
        assert changes['property'] == 'project_title'
        assert changes['prev_value'] == 'Project Title1'
        assert changes['changed_value'] == 'Project Title2'
        assert sz.data['created_by'] == self.crams_log.created_by
