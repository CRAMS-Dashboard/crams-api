# coding=utf-8
"""

"""

from django.urls import path, include
from rest_framework import routers

from crams_collection.views.lookup_api import grant_types
from crams_collection.viewsets.project_contact import ProjectContactViewSet

router = routers.SimpleRouter()

router.register(r'contact', ProjectContactViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('grant_types', grant_types, name='grant_types'),
]
