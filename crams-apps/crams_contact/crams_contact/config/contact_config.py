# coding=utf-8
"""
    Contact Config
"""

# Contact ErbId related
ERBS_CONTACT_ID_UPDATE_FN_MAP = dict()

# Contact System Identifier Email Template
CONTACT_SYSTEM_IDENTIFIER_EMAIL_TEMPLATE = dict()


def update_erb_contact_ids_for_key(contact_obj):
    for id_key_name, fn in ERBS_CONTACT_ID_UPDATE_FN_MAP.items():
        fn(contact_obj, id_key_name)
