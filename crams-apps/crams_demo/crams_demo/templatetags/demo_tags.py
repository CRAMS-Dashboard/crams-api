import json

from django import template
from crams_contact.models import Contact
from crams_contact.models import ContactRole
from crams.models import EResearchBodyIDKey
from crams_contact.models import EResearchContactIdentifier
from crams_collection.models import Project
from crams_collection.models import ProjectID
from crams_collection.models import ProjectContact
from crams_allocation.models import Request

register = template.Library()


@register.filter(name='get_contact_name')
def get_contact_name(email):
    try:
        contact = Contact.objects.get(email=email)
        if contact.given_name:
            return contact.given_name + ' ' + contact.surname
        else:
            return contact.email
    except:
        return email


@register.filter(name='get_user_contact')
def get_user_contact(user_dict):
    email = user_dict
    if email:
        qs = Contact.objects.filter(email__iexact=email)
        if qs.count() > 0:
            return qs.first()

    return None


@register.filter(name='get_name_email')
# tries to get contact full name, if none return email
def get_name_email(updated_by):
    email = updated_by.get('email')
    contact = get_user_contact(email)
    if contact:
        return get_contact_name(contact.email)
    return None


@register.filter(name='filter_project_id')
def get_project_id(project_ids, system_to_search):
    search_tree_hierarchy = ['system', 'key']
    for project_id in project_ids:
        try:
            if DictSearch.search_tree_return_value(
                    search_tree_hierarchy, project_id) == system_to_search:
                return project_id['identifier']
        except Exception:
            pass

    return None


@register.filter(name='get_user_id')
def get_user_id(email, erb_key):
    try:
        erb_id_key = EResearchBodyIDKey.objects.get(key=erb_key)
        erb_contact_id = EResearchContactIdentifier.objects.get(
            contact__email=email, system_id=erb_id_key)

        return erb_contact_id.identifier
    except:
        return None


@register.filter(name='get_group_id')
def get_group_id(project_id, erb_key):
    try:
        erb_id_key = EResearchBodyIDKey.objects.get(key=erb_key)
        project_id = ProjectID.objects.get(
            project_id=project_id, system_id=erb_id_key)

        return project_id.identifier
    except:
        return None


@register.filter(name='filter_project_contact')
def get_project_contact_email(project_contacts, role_name):
    search_tree_hierarchy = ['contact_role']
    for project_contact in project_contacts:
        try:
            if DictSearch.search_tree_return_value(
                    search_tree_hierarchy, project_contact) == role_name:
                return project_contact['contact']['email']

        except Exception:
            pass

    return None


@register.filter(name='get_project_contacts')
def get_project_contacts(project_id):
    # NB: Django ORM distinct is not support by mysql
    # This query will only do a distinct on the email values
    # Therefore the following query will only return the emails and
    # not the expected ProjectContact objects
    pc_list = ProjectContact.objects.filter(
        project_id=project_id).order_by('contact__email').values(
        'contact__email').distinct()

    # get contact from email and append to contact_list
    contact_list = []
    for email in pc_list:
        contact = Contact.objects.get(email=email['contact__email'])
        contact_list.append(contact)

    return contact_list


@register.filter(name='get_project_contacts_by_role')
def get_project_contacts_by_role(prj_obj, role_name):
    # This function fetches the contact roles from deserialized
    # project object, should be used for first time submission since
    # the allocation request is not saved at time calling this function
    proj_json = json.dumps(prj_obj)
    if not prj_obj:
        return None

    prj_contacts = prj_obj.get('project_contacts')

    results = list()
    for prj_cont in prj_contacts:
        if prj_cont.get('contact_role').lower() == role_name.lower():
            results.append(prj_cont.get('contact').get('email'))

    return results


@register.filter(name='get_prj_cont_by_role')
def get_prj_cont_by_role(prj_contacts, role_name):
    results = list()
    for prj_cont in prj_contacts:
        role1 = prj_cont.get('contact_role').lower()
        role_required = role_name.lower()
        if prj_cont.get('contact_role').lower() == role_name.lower():
            contact_dict = prj_cont.get('contact')
            if contact_dict:
                email = contact_dict.get('email')
                if email:
                    results.append(email)

    return results

@register.filter(name='get_req_status_code')
def get_req_status_code(req_id):
    request = Request.object.get(pk=req_id)

    return request.request_status.code


@register.filter(name='display_dc_and_app_contacts')
def display_dc_and_app_contacts(prj_obj):
    proj_json = json.dumps(prj_obj)
    print('----- display_dc_and_app_contacts - proj_json: {}'.format(proj_json))
    try:
        req_id = prj_obj.get('id')
        print('---- request id: {}'.format(req_id))
        if not req_id:    
            return None
    except:
        return None
    # get the requests from project id
    request = Request.objects.get(pk=req_id)
    
    # fetch the data custodians
    dc_list = get_project_contacts_by_role(prj_obj, 'Data Custodian')
    print('----> dc_list: {}'.format(dc_list))
    # fetch the applicant
    app_list = get_project_contacts_by_role(prj_obj, 'Applicant')
    print('----> app_list: {}'.format(app_list))
    # append string result
    result = ''
    i = 0
    while i < len(dc_list):
        result += get_contact_name(dc_list[i])
        if i != len(dc_list)-1:
            result += " \\ "
        i += 1

    if app_list:
        # only add app contact if they are not already in the dc list
        # business rule as of 12-02-2020: there should only be 1 applicant in racmon
        app = app_list[0]
    else:
        # in first submissions project_contacts do not include the applicant
        # need to fetch that from the request updated_by contact field
        # app = prj_obj.get('requests')[0].get('updated_by').get('email')
        app = request.updated_by.email

    if app not in dc_list:
        result += " \\ " + get_contact_name(app)
    print('----> result: {}'.format(result))
    return 'Dear ' + result


@register.filter(name='get_contact_names_by_role')
def get_contact_names_by_role(project_id, role_name):
    project = Project.objects.get(pk=project_id)
    erb = project.requests.first().e_research_system.e_research_body
    project_contacts = ProjectContact.objects.filter(project=project)
    contact_roles = ContactRole.objects.filter(e_research_body=erb, name=role_name)
    contact_names = ''
    if contact_roles:
        contact_role = contact_roles.first()
        project_contacts = project_contacts.filter(contact_role=contact_role)

        for project_contact in project_contacts:
            contact = project_contact.contact
            if contact.given_name:
                contact_name = contact.given_name + ' ' + contact.surname
            else:
                contact_name = contact.email
            contact_names += contact_name + ', '
        contact_names = contact_names.strip()[0:-1]
    return contact_names


@register.filter(name='filter_question_response')
def get_response_for_question(question_responses, question_key):
    search_tree_hierarchy = ['question', 'key']
    for question_response in question_responses:
        try:
            if DictSearch.search_tree_return_value(
                    search_tree_hierarchy, question_response) == question_key:
                return question_response['question_response']

        except Exception:
            pass

    return None


class DictSearch:
    ALL = '*'

    @classmethod
    def search_tree_return_value(cls, search_hierarchy, search_dict):
        """
        Search a multi-level Dictionary for a hierarchy of keys and return the
        value if found.
        Use wildcard '*' at any level for a blind search. The first match will
        be returned for such blind search.

        For example if the dict was
        {
            'question_response': '',
            'question': {
                   'key': 'usagepattern',
                   'question': 'Instance, object storage and volume storage'
                   },
            'id': 10346
        }

        For search_hierarchy ['question', 'key'] and ['*', 'key'] the same
          value will be returned i.e., 'usagepattern'

        But the return value for ['question', '*'] or ['*','*'] is arbitrary.
        Such constructs are useful for determining the minimum tree depth of
        the dictionary

        :param search_hierarchy:
        :param search_dict:
        :return:
        """
        remaining_tree = list(search_hierarchy)
        while remaining_tree:
            if isinstance(search_dict, dict):
                next_node = remaining_tree.pop(0)
                if next_node == DictSearch.ALL:
                    for value_sub_dict in search_dict.values():
                        try:
                            return DictSearch.search_tree_return_value(
                                remaining_tree, value_sub_dict)
                        except Exception:
                            continue
                elif next_node in search_dict:
                    return DictSearch.search_tree_return_value(
                        remaining_tree,
                        search_dict.get(next_node))
                else:
                    raise Exception('Tree Not Found')
            else:
                raise Exception('Tree Not Found')

        return search_dict
