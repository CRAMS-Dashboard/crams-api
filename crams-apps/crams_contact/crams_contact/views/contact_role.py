# coding=utf-8
"""

"""
from rest_framework import mixins
from rest_framework import viewsets

from crams import permissions
from crams_contact import models
from crams_contact.serializers import contact_role


class ContactRoleViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin):
    """
    class ContactRoleViewSet
        Gets all the contact roles for a EResearch Body
    """
    permission_classes = [permissions.IsCramsAuthenticated]
    serializer_class = contact_role.ContactRoleSerializer
    queryset = models.ContactRole.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        if 'erb' in self.request.query_params:
            erb = self.request.query_params['erb']
            queryset = self.queryset.filter(
                e_research_body__name=erb)

        if 'e_research_body' in self.request.query_params:
            erb = self.request.query_params['e_research_body']
            queryset = self.queryset.filter(
                e_research_body__name=erb)

        return queryset
