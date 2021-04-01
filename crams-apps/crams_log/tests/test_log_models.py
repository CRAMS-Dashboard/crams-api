import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from crams_log.models import LogType
from crams_log.models import LogAction
from crams_log.models import CramsLog
from crams_log.models import UserLog


class TestLogModels(TestCase):
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

    def test_log_type_models(self):
        log_type = LogType()
        log_type.log_type = 'test save log_type'
        log_type.name = 'name'
        log_type.description = 'description'
        log_type.save()
        
        # fetch saved obj
        try:
            saved_log_type = LogType.objects.get(pk=log_type.id)
        except:
            saved_log_type = None
        
        # check saved values
        assert saved_log_type
        assert saved_log_type.log_type == 'test save log_type'
        assert saved_log_type.name == 'name'
        assert saved_log_type.description == 'description'

    def test_log_action_models(self):
        log_action = LogAction()
        log_action.action_type = 'test save action_type'
        log_action.name = 'name'
        log_action.description = 'description'
        log_action.save()

        # fetch saved obj
        try:
            saved_log_action = LogAction.objects.get(pk=log_action.id)
        except:
            saved_log_action = None

        # check saved values
        assert saved_log_action
        assert saved_log_action.action_type == 'test save action_type'
        assert saved_log_action.name == 'name'
        assert saved_log_action.description == 'description'

    def test_crams_log_models(self):
        crams_log = CramsLog()
        crams_log.message = 'hello world'
        crams_log.before_json_data = self.before_json_data
        crams_log.after_json_data = self.after_json_data
        crams_log.action = self.log_action
        crams_log.type = self.log_type
        crams_log.created_by = "test@test.com"
        crams_log.save()

        # fetch saved obj
        try:
            saved_crams_log = CramsLog.objects.get(pk=crams_log.id)
        except:
            saved_crams_log = None

        # check saved values
        assert saved_crams_log
        assert saved_crams_log.message == 'hello world'
        assert saved_crams_log.before_json_data == self.before_json_data
        assert saved_crams_log.after_json_data == self.after_json_data
        assert saved_crams_log.action == self.log_action
        assert saved_crams_log.type == self.log_type
        assert saved_crams_log.created_by == "test@test.com"

    def test_user_log_models(self):
        user_log = UserLog()
        user_log.log_parent = self.crams_log
        user_log.crams_user_db_id = 2
        user_log.save()

        # fetch saved values
        try:
            saved_user_log = UserLog.objects.get(pk=user_log.id)
        except:
            saved_user_log = None

        # check saved values
        assert saved_user_log
        assert saved_user_log.log_parent == self.crams_log
        assert saved_user_log.crams_user_db_id == 2
