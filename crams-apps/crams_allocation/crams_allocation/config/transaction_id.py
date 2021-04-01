# coding=utf-8
"""

"""
from rest_framework import exceptions
from crams_allocation.config import allocation_config
from crams.utils.lang_utils import strip_lower

# coding=utf-8
"""
Transaction Id Generators
"""


def generate_transaction_dict_key(erb_system_name, erb_name):
    return strip_lower(erb_system_name) + '%' + strip_lower(erb_name)


def get_transaction_key_for_erb_system(erb_system_obj):
    if erb_system_obj:
        return generate_transaction_dict_key(
            erb_system_obj.name, erb_system_obj.e_research_body.name)
    raise exceptions.ValidationError('e research system is required for generating Transaction Id')


def get_new_transaction_id(request_obj, historical_request):
    if not request_obj:
        raise exceptions.ValidationError(
            'Request obj is required to calculate new Transaction Id')
    erb_system_obj = request_obj.e_research_system
    name = get_transaction_key_for_erb_system(erb_system_obj)
    fn = allocation_config.ERBS_TRANSACTION_ID_FN_MAP.get(name)
    if fn:
        return fn(request_obj, historical_request)

    erb_name = erb_system_obj.e_research_body.name
    return erb_name + '_' + str(request_obj.id).zfill(19)
