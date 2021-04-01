# coding=utf-8
"""

"""
from rest_framework import exceptions

from crams_contact.serializers import contact_serializer
from crams.utils.role import AbstractCramsRoleUtils


class CramsRestRequestData(object):
    # re-named from old ViewsetData(object)
    def __init__(self, viewset_self):
        http_request = viewset_self.request
        self.user = http_request.user
        self.email = None
        if hasattr(http_request.user, 'email'):
            self.email = http_request.user.email
        else:
            raise exceptions.PermissionDenied('User not Authenticated')
        
        context = dict()
        context['request'] = http_request
        self.contact = contact_serializer.ContactSerializer(context=context). \
            fetch_or_create_given_user_as_contact(http_request.user)
        self.user_erb_list = \
            AbstractCramsRoleUtils.get_authorised_e_research_system_list(http_request.user)
        self.crams_id = http_request.query_params.get('crams_id')
        self.request_id = http_request.query_params.get('request_id')
        if self.request_id and not self.request_id.isnumeric():
            raise exceptions.ValidationError(
                'request_id param must be numeric')

        self.current_requested = False
        latest = http_request.query_params.get('fetch_current')
        if latest:
            self.current_requested = True

        self.pk = None
        lookup_url_kwarg = \
            viewset_self.lookup_url_kwarg or viewset_self.lookup_field
        if lookup_url_kwarg and lookup_url_kwarg in viewset_self.kwargs:
            self.pk = viewset_self.kwargs[lookup_url_kwarg]

    def print(self):
        print(self.user, self.pk, self.request_id, self.user_erb_list)
