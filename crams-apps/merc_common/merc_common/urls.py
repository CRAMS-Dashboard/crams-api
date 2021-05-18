"""merc_common URL Configuration

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
from crams.views.auth import rapid_connect_auth_view
from crams.views.funding_body import PrevUserFundingBodyRoleList
from crams.views.lookup_api import EResearchBodySystemViewSet
from crams.views.lookup_api import fb_scheme_list
from crams.views.lookup_api import for_codes
from crams.views.lookup_api import SupportEmailContactViewSet

from django.contrib.auth import views as auth_views
from django.urls import include
from django.urls import path, re_path
from django.views.generic import TemplateView
from rest_framework import routers
from rest_framework.schemas import get_schema_view

router = routers.SimpleRouter()
router.register(r'e_research_body', EResearchBodySystemViewSet, basename='e_r_b')
router.register(r'user_funding_body', PrevUserFundingBodyRoleList, basename='funding_body')
router.register(r'support_email_list', SupportEmailContactViewSet, basename='support-emails')

urlpatterns = [
    # Use the `get_schema_view()` helper to add a `SchemaView` to project URLs.
    #   * `title` and `description` parameters are passed to `SchemaGenerator`.
    #   * Provide view name for use with `reverse()`.
    path('openapi', get_schema_view(
        title="Merc Common API",
        description="API for all things in Merc Common",
        version="1.0.0"
    ), name='openapi-schema'),
    # Route TemplateView to serve Swagger UI template.
    #   * Provide `extra_context` with view name of `SchemaView`.
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),

    path('', include(router.urls)),
    re_path(r'^accounts/login/$', auth_views.LoginView.as_view()),
    re_path(r'^rapid_connect_token_auth', rapid_connect_auth_view),
    re_path(r'funding_scheme/(?P<fb_name>\w+)', fb_scheme_list, name='funding_scheme'),
    re_path(r'for_codes/', for_codes, name='for_codes'),
]
