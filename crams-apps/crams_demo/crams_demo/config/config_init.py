# coding=utf-8
"""
All variables that need to be initialized in crams_demo.settings need to go into this file.
"""
from django.conf import settings
from crams_demo import settings as mod_settings

RDSM_ERB_SYSTEM_LOWER = settings.CRAMS_DEMO_ERB_SYSTEM.lower()
RDSM_ERB_LOWER = settings.CRAMS_DEMO_ERB.lower()

# Enable sending support email to external ticketing system, used to turn-off email send in non Production environment
ENABLE_EXT_SUPPORT_EMAIL = False

# Support EMail
RDSM_SENDER_EMAIL = mod_settings.RDSM_SENDER_EMAIL
RDSM_REPLY_TO_EMAIL = mod_settings.RDSM_REPLY_TO_EMAIL
racmon_support_email_dict = mod_settings.racmon_support_email_dict

# url path for email links
BASE_URL = ''
REQUEST_URL = '/#/allocations/view_request/'
REQ_APPROVAL_URL = '/#/approval/view_request/'
JOIN_URL = '/#/allocations/join_project/'
MEMBER_URL = '/#/allocations/membership/'

# Notification Contact ROLEs
E_RESEARCH_BODY_ADMIN = 'E_RESEARCH_BODY Admin'
E_RESEARCH_BODY_SYSTEM_ADMIN = 'E_RESEARCH_BODY_SYSTEM Admin'
E_RESEARCH_SYSTEM_DELEGATE = 'E_RESEARCH_SYSTEM_DELEGATE'
E_RESEARCH_BODY_SYSTEM_APPROVER = 'E_RESEARCH_BODY_SYSTEM_Approver'
E_RESEARCH_BODY_SYSTEM_PROVISIONER = 'E_RESEARCH_BODY_SYSTEM_Provisioner'
INVITEE = 'Invitee'