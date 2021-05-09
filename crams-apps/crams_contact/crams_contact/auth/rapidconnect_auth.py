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
    request.session["HTTP_REFERER"] = request.META['HTTP_REFERER']
    request.session.modified = True
    return response


@csrf_exempt
def rapid_conn_auth_view(request):
    """
    AAF Rapid Connect auth service POST
    :param request: request should contain a jwt
    :return:
    """
    # decode a jwt using the secret key
    try:
        # fetch the server and port number
        try:
            host = request.headers['Host']
            server = host.split(':')[0]
            port = host.split(':')[1]
        except:
            server = host
            port = None
        
        # set the header HTTPS if port is 443
        if port == '443':
            header = 'https://'
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
    
    response = HttpResponseRedirect(request.session.get("HTTP_REFERER") +
                                    '/#/ks-login' +
                                    query_string)
    response['token'] = crams_token.key
    response['roles'] = crams_token.ks_roles

    return response
