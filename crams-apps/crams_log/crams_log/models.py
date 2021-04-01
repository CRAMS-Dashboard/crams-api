import abc

from django.db import models
from rest_framework import exceptions

from crams_log.constants import log_types, log_actions
from crams.models import User


class LogType(models.Model):
    log_type = models.CharField(
        max_length=23, choices=log_types.TYPE_CHOICES, default=log_types.Project)
    name = models.CharField(max_length=61)
    description = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'crams_log'
        unique_together = ('name', 'log_type')

    def __str__(self):
        return self.name


class LogAction(models.Model):
    action_type = models.CharField(
        max_length=2, choices=log_actions.ACTION_CHOICES, default=log_actions.GENERAL)
    name = models.CharField(max_length=61)
    description = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'crams_log'
        unique_together = ('name', 'action_type')

    def __str__(self):
        return self.name

class CramsLog(models.Model):
    message = models.TextField(blank=True, null=True)

    before_json_data = models.TextField(blank=True, null=True)

    after_json_data = models.TextField(blank=True, null=True)

    creation_ts = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )

    action = models.ForeignKey(LogAction, blank=True, null=True, on_delete=models.DO_NOTHING)

    type = models.ForeignKey(LogType, blank=True, null=True, on_delete=models.DO_NOTHING)

    created_by = models.CharField(max_length=99, blank=True, null=True)

    class Meta:
        app_label = 'crams_log'

    def save(self, *args, **kwargs):
        if self.id:
            raise Exception('Update not allowed')
        return super().save(*args, **kwargs)

    def __str__(self):
        return '{}. {}/{}: {}'.format(self.id, self.action, self.type, self.message)


class AbstractLinkToCramsLog(models.Model):
    log_parent = models.ForeignKey(CramsLog, related_name='%(class)s', on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_log'
        abstract = True

    @classmethod
    @abc.abstractmethod
    def link_log(cls, log_obj, link_obj):
        pass


class UserLog(AbstractLinkToCramsLog):
    crams_user_db_id = models.IntegerField(blank=True, null=True)

    class Meta:
        app_label = 'crams_log'
        unique_together = ('crams_user_db_id', 'log_parent')

    def __str__(self):
        return '{} {}'.format(self.log_parent, self.crams_user_db_id)

    @classmethod
    def link_log(cls, log_obj, user_obj):
        if not isinstance(user_obj, User):
            raise exceptions.ValidationError('User object required for linking to user log')
        crams_user_db_id = user_obj.id
        obj, _ = cls.objects.get_or_create(log_parent=log_obj, crams_user_db_id=crams_user_db_id)
        return obj

    @classmethod
    def fetch_log_qs(cls, crams_user_db_id):
        return cls.objects.filter(crams_user_db_id=crams_user_db_id)
