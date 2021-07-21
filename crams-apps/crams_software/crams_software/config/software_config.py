from crams.models import EResearchBody
from django.conf import settings

# Configurable fields for Software Products
def get_erb_contact_id_key(erb_name):
    return settings.ERB_CONTACT_ID_KEY[erb_name]

def get_erb_software_group_id_key(erb_name):
    return settings.ERB_SOFTWARE_GROUP_ID_KEY[erb_name]

# Email Processing Module by ERB System,
#    -dict key is tuple (erb_system_obj.name, erb_system_obj.e_reserch_body.name)
ERB_Software_Email_fn_dict = dict()

def get_email_processing_fn(erb_email_dict, erb_obj):
    print('----- erbs_email_dict:{}'.format(erb_email_dict))
    print('----- erb_system_obj:{}'.format(erb_obj))
    if not isinstance(erb_obj, EResearchBody):
        return None
    return erb_email_dict.get(erb_obj.name.lower())
