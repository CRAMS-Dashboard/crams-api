# coding=utf-8
"""
 auth.py
"""
from crams.models import UserEvents
from crams_log.log_events import login
from django.contrib.auth import authenticate
from rest_framework.authtoken import views
from rest_framework.response import Response

from crams_contact.serializers.contact_erb_roles import ContactErbRoleSerializer


class CramsBasicLoginAuthToken(views.ObtainAuthToken):
    """

    """

    def post(self, request):
        """
        post method
        :param request:
        :return:
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            # msg = 'User logged in with valid User/Password'
            # login.log_user_login(request, user, msg)
            # UserEvents.objects.create(
            #     created_by=user,
            #     event_message=msg
            # )

            crams_token = ContactErbRoleSerializer.setup_crams_token_and_roles(user)

            response = Response({'token': crams_token.key})
            response['token'] = crams_token.key
            response['roles'] = crams_token.ks_roles
            return response

        return Response('Login fail')

# obtain_auth_token = CramsBasicLoginAuthToken.as_view()
