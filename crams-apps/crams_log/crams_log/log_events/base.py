# coding=utf-8
"""

"""

from crams_log import models


class CramsLogModelUtil:
    @classmethod
    def create_new_log(cls, before_json, after_json, log_type, action, message, user_obj=None):
        obj = models.CramsLog()
        obj.before_json_data = before_json
        obj.after_json_data = after_json
        obj.type = log_type
        obj.action = action
        obj.message = message
        if user_obj:
            obj.created_by = user_obj.email
        obj.save()

        return obj
