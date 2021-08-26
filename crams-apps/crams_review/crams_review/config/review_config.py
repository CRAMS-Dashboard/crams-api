from crams.models import EResearchBody


# Email Processing Module by ERB System,
#    -dict key is tuple (erb_system_obj.name, erb_system_obj.e_reserch_body.name)
ERB_Review_Email_fn_dict = dict()

def get_email_processing_fn(erb_email_dict, erb_obj):
    print('----- erbs_email_dict:{}'.format(erb_email_dict))
    print('----- erb_system_obj:{}'.format(erb_obj))
    if not isinstance(erb_obj, EResearchBody):
        return None
    return erb_email_dict.get(erb_obj.name.lower())