# coding=utf-8
"""

"""
from crams_log import models


def fetch_log_action(action_type, action_name):
    obj, created = models.LogAction.objects.get_or_create(action_type=action_type, name=action_name)
    if created:
        obj.description = action_type + ': ' + action_name
        obj.save()
    return obj


def fetch_log_type(log_type, log_name):
    obj, created = models.LogType.objects.get_or_create(log_type=log_type, name=log_name)
    if created:
        obj.description = log_type + ': ' + log_name
        obj.save()
    return obj
