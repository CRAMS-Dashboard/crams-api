# coding=utf-8
"""

"""

from crams.config import config_init
from crams.utils.lang_utils import strip_lower


eSYSTEM_NECTAR = 'NeCTAR'
NECTAR_LOWER = strip_lower(eSYSTEM_NECTAR)

# Research Body Reply-to Email Map
config_init.eSYSTEM_REPLY_TO_EMAIL_MAP[NECTAR_LOWER] = \
    settings.NECTAR_NOTIFICATION_REPLY_TO

SYSTEM_APPLICANT_DEFAULT_ROLE[NECTAR_LOWER] = db.APPLICANT


