# coding=utf-8
"""

"""

# Create your views here.

from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response

from crams import permissions
from crams.utils import django_utils
from crams_contact.models import Contact
from crams_contact.serializers import contact_serializer
from crams_contact.serializers.base_contact_serializer import BaseContactSerializer


class ContactViewSet(django_utils.CramsModelViewSet):
    """
    class ContactViewSet
    """
    permission_classes = [permissions.IsCramsAuthenticated]
    queryset = Contact.objects.all()
    serializer_class = contact_serializer.ContactSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('given_name', 'surname', 'email')

    @action(detail=False, url_path='(?P<email>[^@]+@[^@]+.[^@\d.]+)')
    def search_by_email(self, request, email=None):
        if email:
            context = {'request': request}
            queryset = self.serializer_class.search_contact_get_queryset(email=email)
            serializer = self.serializer_class(queryset, many=True, context=context)
            return Response(serializer.data)
        return Response(dict())


class AdminContactViewSet(ContactViewSet):
    """
    class Admin ContactViewSet
    """
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsCramsAdmin]
    queryset = Contact.objects.all()
    serializer_class = BaseContactSerializer
