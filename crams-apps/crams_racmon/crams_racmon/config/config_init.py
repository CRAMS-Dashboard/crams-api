# coding=utf-8
"""
All variables that need to be initialized in crams_racmon.settings need to go into this file.
"""
from django.conf import settings

RDSM_ERB_SYSTEM_LOWER = settings.CRAMS_DEMO_ERB_SYSTEM.lower()
RDSM_ERB_LOWER = settings.CRAMS_DEMO_ERB.lower()

# Enable sending support email to external ticketing system, used to turn-off email send in non Production environment
ENABLE_EXT_SUPPORT_EMAIL = False

# Support EMail
RDSM_REPLY_TO_EMAIL = "helpdesk@crams.com"
racmon_support_email_dict = {
    'key': 'CRAMS',
    'email': 'helpdesk@crams.com'}
