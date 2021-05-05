# coding=utf-8
"""
 rapid connect authentication related code
"""
import jwt
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import exceptions as rest_exceptions
from rest_framework.decorators import api_view
from django.conf import settings

# from crams.common.utils import log_process
from crams.utils.lang_utils import strip_lower
from crams.models import User
# from crams.models import UserEvents
from crams_contact.serializers.contact_erb_roles import ContactErbRoleSerializer


@api_view(['GET'])
def redirect_to_rapid_conn(request):
    """
    redirect to AAF Rapid Connect
    :param request:
    :return:
    """
    response = HttpResponseRedirect(settings.AAF_RAPID_CONN_URL)
    # save the origin address of where the request came from
    # the origin address is used to redirect back after auth is successful
    response.set_cookie('HTTP_REFERER', request.META['HTTP_REFERER'])

    return response


@csrf_exempt
def rapid_conn_auth_view(request):
    """
    AAF Rapid Connect auth service POST
    :param request: request should contain a jwt
    :return:
    """

    # decode a jwt using the secret key
    server = request.META['SERVER_NAME']
    try:
        # set header for url
        if request.is_secure():
            header = 'https://'
            if not request.META['SERVER_PORT'] == '443':
                server += ':' + request.META['SERVER_PORT']
        else:
            header = 'http://'

        verified_jwt = jwt.decode(
            request.POST['assertion'], settings.AAF_SECRET,
            audience=header + server,
            options={'verify_iat': False})
    except:
        raise rest_exceptions.AuthenticationFailed(
            'Invalid jwt from rapid connect, contact Support')

    # get user details from jwt
    email = verified_jwt['https://aaf.edu.au/attributes']['mail']
    email = strip_lower(email)

    # user name attributes
    display_name = verified_jwt['https://aaf.edu.au/attributes']['displayname']
    first_name = verified_jwt['https://aaf.edu.au/attributes']['givenname']
    last_name = verified_jwt['https://aaf.edu.au/attributes']['surname']

    # verify user on crams
    try:
        user = User.objects.get(email=email,
                                first_name=first_name,
                                last_name=last_name)

    # return multiple users with the same email
    except User.MultipleObjectsReturned:
        raise rest_exceptions.AuthenticationFailed(
            'Multiple UserIds exist for User, contact Support')

    # User does not exist in CRAMS
    except User.DoesNotExist:
        user, created = User.objects.get_or_create(email=email, username=email)

    #log login
    # msg = 'User logged in with valid AAF credentials'
    # log_process.log_user_login(request, user, msg)
    # events = UserEvents(
    #     created_by=user,
    #     event_message=msg
    # )
    # events.save()

    # Generate CramsToken
    crams_token = ContactErbRoleSerializer.setup_crams_token_and_roles(user)
    query_string = "?username=%s&rest_token=%s" % (user.username,
                                                   crams_token.key)

    response = HttpResponseRedirect(request.COOKIES.get('HTTP_REFERER') +
                                    '/#/ks-login' +
                                    query_string)
    response['token'] = crams_token.key
    response['roles'] = crams_token.ks_roles

    return response
