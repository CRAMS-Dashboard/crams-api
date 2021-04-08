# coding=utf-8
"""

"""

from crams_allocation.config.allocation_config import EXTEND_ON_QUOTA_CHANGE
from django.conf import settings

# TODO: move the sample ERB system sqls for CRAMS-ERB and CRAMS-ERB-SYS to this module (from merc-common)
EXTEND_ON_QUOTA_CHANGE.append(settings.CRAMS_DEMO_ERB_SYSTEM.lower())