# coding=utf-8
"""

"""

from crams_allocation.config.allocation_config import EXTEND_ON_QUOTA_CHANGE
from crams_allocation.config.allocation_config import ERB_System_Allocation_Submit_Email_fn_dict
from crams_allocation.config.allocation_config import ADMIN_ALERT_DATA_SENSITIVE
from crams_allocation.config.allocation_config import ADMIN_ALERT_QUESTION_KEYS

from crams_racmon.notifications.submit_allocation import submit_allocation_emails
from django.conf import settings

RDSM_ERB_SYSTEM_LOWER = settings.CRAMS_DEMO_ERB_SYSTEM.lower()
RDSM_ERB_LOWER = settings.CRAMS_DEMO_ERB.lower()

# TODO: move the sample ERB system sqls for CRAMS-ERB and CRAMS-ERB-SYS to this module (from merc-common)
EXTEND_ON_QUOTA_CHANGE.append(settings.CRAMS_DEMO_ERB_SYSTEM.lower())

# Enable sending support email to external ticketing system, used to turn-off email send in non Production environment
ENABLE_EXT_SUPPORT_EMAIL = True
fn_key = (RDSM_ERB_SYSTEM_LOWER, settings.CRAMS_DEMO_ERB.lower())
ERB_System_Allocation_Submit_Email_fn_dict[fn_key] = submit_allocation_emails
print('------ racmon fn_key: {}'.format(fn_key))
print('------ > ERB_System_Allocation_Submit_Email_fn_dict[fn_key]: {}'.format(ERB_System_Allocation_Submit_Email_fn_dict))
# Support EMail
RDSM_REPLY_TO_EMAIL = "xiaoming.yu@monash.edu"
support_email_dict = {'key': 'CRAMS',
                      'email': 'xiaoming.yu@monash.edu'}

# admin email alert when data sensitive flag changes
ADMIN_ALERT_DATA_SENSITIVE.append(RDSM_ERB_LOWER)

# admin email alert when question key changes
ADMIN_ALERT_QUESTION_KEYS.append(
    {RDSM_ERB_LOWER: 'racm_electronic_inf_class'})
ADMIN_ALERT_QUESTION_KEYS.append(
    {RDSM_ERB_LOWER: 'racm_data_migration_assistance'})
