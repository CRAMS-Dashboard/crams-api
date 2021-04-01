# coding=utf-8
"""
    Validate Config
"""
import logging
import importlib
from django.conf import settings
from crams.utils import role
from crams.constants import db

MINIMUM = 'minimum'
MAXIMUM = 'maximum'

# Research Body Reply-to Email Map
eSYSTEM_REPLY_TO_EMAIL_MAP = dict()

# Disallow admin Provider role for the following ERB Systems
ERBS_PROVIDER_DISALLOW_LIST = list()
# Disallow admin Provider role for the following Eresearch Body
ERB_PROVIDER_DISALLOW_LIST = list()

# Project ErbId related dict
#     key: (id_key_name, erb_name)
#     value: (generator_fn, validate_fn)
ERBS_PROJECT_ID_UPDATE_FN_MAP = dict()

# Contact ErbId related
ERBS_CONTACT_ID_UPDATE_FN_MAP = dict()

# EResearchSystem Delegate Question Key Map
DELEGATE_QUESTION_KEY_MAP = dict()

# Contact System Identifier Email Template
CONTACT_SYSTEM_IDENTIFIER_EMAIL_TEMPLATE = dict()

# Update User Visibility
CRAMS_DEFAULT_UPDATED_BY_VISIBILTY_ROLE = [role.AbstractCramsRoleUtils.APPROVER_ROLE_KEY,
                                           role.AbstractCramsRoleUtils.PROVIDER_ROLE_KEY]
DEFAULT_UPDATED_BY_PREFIX = ''  # 'Authorised User'
UPDATED_BY_VISIBLE_ROLEGRP_FOR_ERB_LOWER = dict()

# Allocation list API requires returning of ERB system specific Project Ids like HPC_POSIX_GROUP_ID
ALLOCATION_LIST_ERB_IDKEY_DICT = dict()

# Each Role can be set to occur a minimum and maximum number of times.
# A value of 0 in max implies unlimited
CONTACT_ROLE_VALID_COUNT = dict()
CONTACT_ROLE_VALID_COUNT[db.eSYSTEM_NECTAR] = {db.CHIEF_INVESTIGATOR: (1, 1)}
CONTACT_ROLE_VALID_COUNT[db.eSYSTEM_VICNODE] = {db.DATA_CUSTODIAN: (1, 1),
                                                db.TECHNICAL_CONTACT: (1, 0)}

# for config_settings in settings.CRAMS_APP_CONFIG_LIST:
#     try:
#         importlib.import_module(config_settings)  # noqa
#     except ImportError:
#         logging.debug("config file not found: {}".format(config_settings))


def get_min_max_dict(min=None, max=None):
    ret_dict = dict()
    if min:
        ret_dict[MINIMUM] = min
    if max:
        ret_dict[MAXIMUM] = max
    return ret_dict
