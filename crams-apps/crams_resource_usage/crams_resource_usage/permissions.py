# coding=utf-8
"""

"""
from rest_framework import permissions, exceptions

from django.conf import settings


class IsBatchIngestUser(permissions.IsAuthenticated):
    """
    Batch User validation. Only authenticated users with username specified
    in settings will be allowed to ingest
    """
    message = 'User does not have batch update privilege.'

    def has_permission(self, request, view):
        """
        User must be specfied in settings.BATCH_INGEST_USERS
        :param request:
        :param view:
        :return:
        """
        if super().has_permission(request, view):
            return request.user.username in settings.BATCH_INGEST_USERS
        return False
