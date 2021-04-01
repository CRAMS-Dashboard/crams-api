# coding=utf-8
"""

"""
from crams import permissions
from crams_collection.viewsets.project_contact import AdminProjectContactViewSet
from crams_contact.models import Contact
from crams_contact.serializers.base_contact_serializer import BaseContactSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

from crams_allocation.serializers import contact_project_list


class AdminProjectRequestContactViewSet(AdminProjectContactViewSet):
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsCramsAdmin]
    queryset = Contact.objects.all()
    serializer_class = BaseContactSerializer

    @action(detail=False, url_path='(?P<contact_id>\d+)/list/project')
    def get_contact_projects(self, request, contact_id):
        context = {'request': request}
        queryset = self.serializer_class.search_contact_get_queryset(pk=contact_id)
        serializer = contact_project_list.AdminContactAllocationListSerializer(
            queryset.first(), context=context)
        return Response(serializer.data)
