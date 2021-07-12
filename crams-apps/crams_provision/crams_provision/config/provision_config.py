from crams.models import EResearchBodySystem


# Email Processing Module by ERB System,
#    -dict key is tuple (erb_system_obj.name, erb_system_obj.e_reserch_body.name)
ERB_System_Partial_Provision_Email_fn_dict = dict()

def get_email_processing_fn(erbs_email_dict, erb_system_obj):
    print('----- erbs_email_dict:{}'.format(erbs_email_dict))
    print('----- erb_system_obj:{}'.format(erb_system_obj))
    if not isinstance(erb_system_obj, EResearchBodySystem):
        return None
    f_key = (erb_system_obj.name.lower(), erb_system_obj.e_research_body.name.lower())
    return erbs_email_dict.get(f_key)