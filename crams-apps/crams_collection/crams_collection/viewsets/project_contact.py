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
from crams_collection.serializers import contact_project_list
from crams_contact.serializers.base_contact_serializer import BaseContactSerializer
from crams_contact.serializers.contact_serializer import ContactSerializer
from crams_contact.views import contact as contact_view


class ProjectContactViewSet(contact_view.ContactViewSet):
    """
    class ContactViewSet
    """
    permission_classes = [permissions.IsCramsAuthenticated]
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('given_name', 'surname', 'email')

    @action(detail=False, url_path='(?P<email>[^@]+@[^@]+.[^@\d.]+)')
    def search_by_email(self, request, email=None):
        if email:
            context = {'request': request}
            queryset = self.serializer_class.search_contact_get_queryset(
                email=email)
            serializer = contact_project_list.ContactProjectListSerializer(
                queryset, context=context, many=True)
            return Response(serializer.data)
        return Response(dict())


class AdminProjectContactViewSet(django_utils.CramsModelViewSet):
    """
    class Admin ContactViewSet
    """
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsCramsAdmin]
    queryset = Contact.objects.all()
    serializer_class = BaseContactSerializer

    @action(detail=False, url_path='(?P<email>[^@]+@[^@]+.[^@\d.]+)')
    def search_by_email(self, request, email=None):
        if email:
            context = {'request': request}
            queryset = self.serializer_class.search_contact_get_queryset(email=email)
            serializer = contact_project_list.ContactProjectListSerializer(
                queryset, context=context, many=True)
            return Response(serializer.data)
        return Response(dict())

    @action(detail=False, url_path='(?P<contact_id>\d+)/list/project')
    def get_contact_projects(self, request, contact_id):
        context = {'request': request}
        queryset = self.serializer_class.search_contact_get_queryset(pk=contact_id)
        serializer = contact_project_list.ContactProjectListSerializer(
            queryset.first(), context=context)
        return Response(serializer.data)
