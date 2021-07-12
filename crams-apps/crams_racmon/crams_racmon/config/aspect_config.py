# coding=utf-8
"""

"""
from crams_racmon.config.config_init import RDSM_ERB_LOWER, RDSM_ERB_SYSTEM_LOWER

from crams_allocation.config.allocation_config import EXTEND_ON_QUOTA_CHANGE
from crams_allocation.config.allocation_config import ERB_System_Allocation_Submit_Email_fn_dict
from crams_allocation.config.allocation_config import ADMIN_ALERT_DATA_SENSITIVE
from crams_allocation.config.allocation_config import ADMIN_ALERT_QUESTION_KEYS
from crams_member.config.member_config import ERB_System_Membership_Email_fn_dict
from crams_provision.config.provision_config import ERB_System_Partial_Provision_Email_fn_dict
from crams_racmon.notifications.submit_allocation import submit_allocation_emails
from crams_racmon.notifications.membership import send_membership_notification
from crams_racmon.notifications.racmon_notification_utils import RacmonAllocationNotificationUtils as ra

from django.conf import settings

# TODO: move the sample ERB system sqls for CRAMS-ERB and CRAMS-ERB-SYS to this module (from merc-common)
EXTEND_ON_QUOTA_CHANGE.append(settings.CRAMS_DEMO_ERB_SYSTEM.lower())


fn_key = (RDSM_ERB_SYSTEM_LOWER, settings.CRAMS_DEMO_ERB.lower())
ERB_System_Allocation_Submit_Email_fn_dict[fn_key] = submit_allocation_emails
ERB_System_Membership_Email_fn_dict[fn_key] = send_membership_notification
ERB_System_Partial_Provision_Email_fn_dict[fn_key] = ra.send_partial_provision_notification


# admin email alert when data sensitive flag changes
ADMIN_ALERT_DATA_SENSITIVE.append(RDSM_ERB_LOWER)

# admin email alert when question key changes
ADMIN_ALERT_QUESTION_KEYS.append(
    {RDSM_ERB_LOWER: 'racm_electronic_inf_class'})
ADMIN_ALERT_QUESTION_KEYS.append(
    {RDSM_ERB_LOWER: 'racm_data_migration_assistance'})
