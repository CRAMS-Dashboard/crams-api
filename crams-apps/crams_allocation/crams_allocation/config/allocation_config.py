# coding=utf-8
"""
    Validate Config
"""
import logging
import importlib
from django.conf import settings
from crams.constants import db
from crams.utils.role import AbstractCramsRoleUtils
from crams.utils.lang_utils import strip_lower

from crams_allocation.constants.db import ADMIN_STATES

# CONTEXT_PARAMS
CRAMS_REQUEST_PARENT = 'CRAMS_REQUEST_PARENT'

# Enable sending support email to external ticketing system
ENABLE_EXT_SUPPORT_EMAIL = False

REQUEST_STORAGE_PRODUCT_PER_SYSTEM = dict()

# review date is calculated at the provisioned date plus review_period in
# months gives the actual review date for project.
eSYSTEM_REVIEW_PERIOD_MAP = dict()

# how months before the review period to notify admin to for review
eSYSTEM_REVIEW_NOTIFY_PERIOD_MAP = dict()

# Transaction Id related
ERBS_TRANSACTION_ID_FN_MAP = dict()

# EResearchSystem Delegate Question Key Map
DELEGATE_QUESTION_KEY_MAP = dict()

# RACMON allocation requests will go from "Provisioned" to "Update/Extended"
# only when product quota has changed, added or removed.
# All other project/request meta data fields change will move the status to
# "Application Updated"
EXTEND_ON_QUOTA_CHANGE = []

# admin email alert when data sensitive flag changes
ADMIN_ALERT_DATA_SENSITIVE = []

# admin email alert when question key changes
ADMIN_ALERT_QUESTION_KEYS = []

# storage product that have negative allocated gb values to indicate unlimited
STORAGE_PRODUCT_ALLOC_NEG = []

RESTRICTED_ADMIN_STATUS = ADMIN_STATES

MINIMUM = 'minimum'
MAXIMUM = 'maximum'

NECTAR_LOWER = strip_lower(db.eSYSTEM_NECTAR)

# Research Body Reply-to Email Map
eSYSTEM_REPLY_TO_EMAIL_MAP = dict()
eSYSTEM_REPLY_TO_EMAIL_MAP[NECTAR_LOWER] = \
    settings.NECTAR_NOTIFICATION_REPLY_TO

# Project ErbId related dict
#     key: (id_key_name, erb_name)
#     value: (generator_fn, validate_fn)
ERBS_PROJECT_ID_UPDATE_FN_MAP = dict()

# Contact ErbId related
ERBS_CONTACT_ID_UPDATE_FN_MAP = dict()

# Contact System Identifier Email Template
CONTACT_SYSTEM_IDENTIFIER_EMAIL_TEMPLATE = dict()

# Update User Visibility
CRAMS_DEFAULT_UPDATED_BY_VISIBILTY_ROLE = [AbstractCramsRoleUtils.APPROVER_ROLE_KEY,
                                           AbstractCramsRoleUtils.PROVIDER_ROLE_KEY]
DEFAULT_UPDATED_BY_PREFIX = ''  # 'Authorised User'
UPDATED_BY_VISIBLE_ROLEGRP_FOR_ERB_LOWER = dict()

# Applicant Default role, per system
SYSTEM_APPLICANT_DEFAULT_ROLE = dict()
SYSTEM_APPLICANT_DEFAULT_ROLE[NECTAR_LOWER] = db.APPLICANT

# Allocation list API requires returning of ERB system specific Project Ids like HPC_POSIX_GROUP_ID
ALLOCATION_LIST_ERB_IDKEY_DICT = dict()

# External Support email system EResearchBodyIDKey
EXTERNAL_SUPPORT_EMAIL = dict()

for config_settings in settings.CRAMS_APP_CONFIG_LIST:
    try:
        importlib.import_module(config_settings)  # noqa
    except ImportError:
        logging.debug("config file not found: {}".format(config_settings))


def get_min_max_dict(min=None, max=None):
    ret_dict = dict()
    if min:
        ret_dict[MINIMUM] = min
    if max:
        ret_dict[MAXIMUM] = max
    return ret_dict
