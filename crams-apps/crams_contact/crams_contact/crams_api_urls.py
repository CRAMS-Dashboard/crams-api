"""crams_contact URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from crams_contact.auth.auth_api import CramsBasicLoginAuthToken
from crams_contact.auth.user_roles_api import CurrentUserRolesView
from crams_contact.auth import rapidconnect_auth 
from crams_contact.views.contact import ContactViewSet
from crams_contact.views.contact_role import ContactRoleViewSet
from crams_contact.views.organisation import DepartmentViewSet
from crams_contact.views.organisation import FacultyViewSet
from crams_contact.views.organisation import OrganisationViewSet
from django.conf.urls import url

router = routers.SimpleRouter()
router.register(r'contact_role', ContactRoleViewSet)
router.register(r'department', DepartmentViewSet)
router.register(r'faculty', FacultyViewSet)
router.register(r'organisation', OrganisationViewSet)
router.register(r'searchcontact', ContactViewSet)

urlpatterns = [
    path('', include(router.urls)),
    url(r'api-token-auth', CramsBasicLoginAuthToken.as_view(), name='api_token_auth'),
    url(r'user_roles', CurrentUserRolesView.as_view(), name='user_roles'),
    # rapid connect authentication related
    url(r'redirect_to_rapid_conn', rapidconnect_auth.redirect_to_rapid_conn),
    url(r'rapid_conn_auth', rapidconnect_auth.rapid_conn_auth_view),
]
