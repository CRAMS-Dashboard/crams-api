# coding=utf-8
"""

"""
from rest_framework import exceptions

from crams.utils import date_utils


def extract_http_query_params(param_validationfnList_dict, http_request_obj):
    ret_dict = dict()

    for param, fn_list in param_validationfnList_dict.items():
        if param in http_request_obj.query_params:
            value = http_request_obj.query_params.get(param)
            for fn in fn_list:
                value = fn(param, value)
            ret_dict[param] = value
    return ret_dict


def extract_validate_post_params(
        param_validationfnList_dict, http_request_obj):
    ret_dict = dict()
    post_data = http_request_obj.data
    for param, fn_list in param_validationfnList_dict.items():
        if param in post_data:
            value = post_data.get(param)
            for fn in fn_list:
                value = fn(param, value)
            ret_dict[param] = value
    return ret_dict


def is_required_param_function(param_name, value):
    if value is None:
        raise exceptions.ValidationError(
            '{} param is required'.format(param_name))
    return value


def is_param_numeric_function(param_name, value):
    if not value.isnumeric():
        raise exceptions.ValidationError(
            '{} param must be numeric'.format(param_name))
    return value


def is_param_date_function(param_name, value):
    try:
        date_ts_obj = date_utils.parse_datetime_from_str(value)
        return date_ts_obj.date()
    except ImportError:
        msg = '{}: date format incorrect'.format(param_name)
        raise exceptions.ValidationError(msg)
