# coding=utf-8
"""

"""

from crams_log.log_events import base
from crams_log.constants import log_actions, log_types
from crams_log.utils import lookup_utils
from crams_log.models import UserLog


def log_user_login(http_request_obj, user_obj, message=None, override_referer=None):
    if not message:
        message = 'User logged in'
    action = lookup_utils.fetch_log_action(log_actions.LOGIN, 'Client Login')

    referer = override_referer or http_request_obj.COOKIES.get('HTTP_REFERER')
    if not referer:
        referer = 'Referer Unknown'
    log_type = lookup_utils.fetch_log_type(log_types.API, referer)

    before_json = None
    after_json = {
        'REMOTE_ADDR': http_request_obj.META.get('REMOTE_ADDR'),
        'REMOTE_PORT': http_request_obj.META.get('REMOTE_PORT'),
        'REMOTE_USER': http_request_obj.META.get('REMOTE_USER'),
        'HTTP_REFERER': referer
    }
    log_obj = base.CramsLogModelUtil.create_new_log(before_json, after_json, log_type, action, message, user_obj)

    # link log to relevant User and Contact
    if user_obj:
        UserLog.link_log(log_obj, user_obj=user_obj)
        # if contact:
        #     crams_log_utils.LogUtils.link_contact_log(log_obj, crams_contact_db_id=contact.id)

    return log_obj
