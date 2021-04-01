from django import template

from crams_contact.models import ContactRole

register = template.Library()


@register.filter(name="get_contact_from_role")
def get_contact_from_role(project_contacts, contact_role):
    # get contact role from erb and role name
    # assumption is the role specified for project should have only 1 contact
    # if the role in the project has more than 1 contact
    # use the other function to get a list of contacts
    try:
        # get the first contact that matches
        contact = project_contacts.filter(
            contact_role__name__iexact=contact_role).first().contact

        # get the full name of contact if possible
        if contact.given_name and contact.surname:
            full_name = "{} {}".format(
                contact.given_name, contact.surname)
            if contact.title:
                full_name = "{} {}".format(
                    contact.title, full_name)

            return full_name

        # if full name can not be retrieved default to the email
        return contact.email
    except:
        return ""


@register.filter(name="get_contact_list_from_role")
def get_contact_list_from_role(project_contacts, contact_role):
    try:
        prj_ct_list = project_contacts.filter(
            contact_role__name__iexact=contact_role)
        contact_list = list()
        for prj_ct in prj_ct_list:
            contact_list.append(prj_ct.contact)

        return contact_list
    except:
        return ""


@register.filter(name="get_retention_period")
def get_retention_period(request):
    current_req = request
    if request.current_request != None:
        current_req = request.current_request

    for q_resp in current_req.request_question_responses.all():
        if q_resp.question.key == 'racm_data_retention_period':
            return q_resp.question_response

    # if nothing found return None
    return None


