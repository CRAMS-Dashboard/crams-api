from django.utils.translation import ugettext_lazy as _
from rest_framework import authentication, exceptions
from crams import models


class CramsTokenAuthentication(authentication.TokenAuthentication):
    message = _('User does not hold valid CramsToken.')

    def authenticate(self, request):
        auth_tuple = super().authenticate(request)
        if auth_tuple:
            try:
                user, token = auth_tuple
                crams_token = models.CramsToken.objects.get(user=user)
                if crams_token.is_expired():
                    raise exceptions.AuthenticationFailed(self.message)
            except Exception as e:
                raise exceptions.AuthenticationFailed(_('{}'.format(e)))
        return auth_tuple
