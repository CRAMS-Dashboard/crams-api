"""

"""
from django.conf import settings
from crams import models as crams_models
from crams_contact import models as contact_models
from django.contrib.auth import get_user_model

NORM_PASS = settings.NORM_PASS
test_user_emails = settings.TEST_USERS
erb_admin_emails = settings.ERB_ADMINS
erb_system_admins = settings.ERB_SYSTEM_ADMINS
erb_approvers = settings.ERB_APPROVERS
erb_providers = settings.ERB_PROVIDERS

email_dict = {'crams-erb': test_user_emails}

admin_dict = {'crams-erb': erb_admin_emails}

admin_erbs_dict = {
    'crams-erb': {
        'crams-erb-sys': erb_system_admins
    }
}

approver_erbs_dict = {
    'crams-erb': {
        'crams-erb-sys': erb_approvers
    }
}

provider_dict = {'crams': erb_providers}


def get_erb_provider_name(erb_name):
    ret_pname = erb_name
    if erb_name == 'crams-erb':
        ret_pname = 'crams'
    return ret_pname


for erb_name, email_list in admin_dict.items():
    provider_name = get_erb_provider_name(erb_name)
    p_list = provider_dict.get(provider_name)
    p_set = set(p_list + admin_dict.get(erb_name))
    provider_dict[erb_name] = list(p_set)


def setup_user_password(email, password):
    User = get_user_model()
    user, created = User.objects.get_or_create(email=email, username=email)
    if created:
        print('created', user)
    if password:
        user.set_password(password)
        user.save()
    return user


def set_django_admin(email):
    try:
        User = get_user_model()
        user_obj = User.objects.get(email=email)
        user_obj.is_staff = True
        user_obj.is_superuser = True
        user_obj.save()
    except User.DoesNotExist:
        pass


def setup_user_roles():
    for erb_name, email_tuple_list in email_dict.items():
        erb_obj = crams_models.EResearchBody.objects.get(name__iexact=erb_name)
        for email_tp in email_tuple_list:
            email = email_tp[0]
            password = email_tp[1]
            setup_user_password(email, password)
            # set as Django admin if true
            try:
                if email_tp[2]:
                    set_django_admin(email)
            except IndexError:
                pass
            setup_erb_user_roles(erb_obj, email)


def setup_erb_user_roles(erb_obj, email):
    erb_name = erb_obj.name.lower()
    contact, created = contact_models.Contact.objects.get_or_create(email=email)
    if created:
        print('', '  contact create', contact.id, contact.email)
    name = email.split('@')
    if not contact.given_name:
        contact.given_name = name[0]
        contact.save()
    if not contact.surname:
        contact.surname = name[1]
        contact.save()

    qs = contact_models.CramsERBUserRoles.objects.filter(contact=contact, role_erb=erb_obj)
    if qs.count() > 1:
        qs.delete()  # duplicate erb roles, delete them all
    erb_role, created = contact_models.CramsERBUserRoles.objects.get_or_create(
        contact=contact, role_erb=erb_obj)

    if created:
        print('', '  erb role create', erb_role.id, erb_role.role_erb)

    if email in admin_dict.get(erb_name, list()):
        erb_role.is_erb_admin = True

    if email in provider_dict.get(erb_name, list()):
        p_name = get_erb_provider_name(erb_name)
        provider_obj = crams_models.Provider.objects.get(name__iexact=p_name)
        erb_role.providers.set([provider_obj])

    role_erbs_admin = set()
    for erbs, email_list in admin_erbs_dict.get(erb_name, dict()).items():
        erbs_obj = erb_obj.systems.get(name__iexact=erbs)
        if email in email_list:
            role_erbs_admin.add(erbs_obj)
    erb_role.admin_erb_systems.set(role_erbs_admin)

    approver_erbs = set()
    for erbs, email_list in approver_erbs_dict.get(erb_name, dict()).items():
        erbs_obj = erb_obj.systems.get(name__iexact=erbs)
        if email in email_list:
            approver_erbs.add(erbs_obj)
    erb_role.approver_erb_systems.set(approver_erbs)

    erb_role.save()
    print('Setup test user done!', email)


"""
from crams_api.local import setup_test_users
setup_test_users.setup_user_roles()
"""
