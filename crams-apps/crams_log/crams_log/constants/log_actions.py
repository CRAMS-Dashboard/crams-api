# coding=utf-8
"""
    Log Action constants
"""

# Log Actions
LOGIN = 'LI'
GENERAL = 'GR'
STATUS_CHANGE = 'SC'
PROVISION = 'PR'
UPDATE_FORM = 'EF'
ACTION_CHOICES = ((GENERAL, 'General'),
                  (LOGIN, 'Login'),
                  (STATUS_CHANGE, 'Request Status Change'),
                  (PROVISION, 'Product Provision'),
                  (UPDATE_FORM, 'Form Update')
                  )

