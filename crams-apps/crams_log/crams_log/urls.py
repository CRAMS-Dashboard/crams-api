"""crams_log URL Configuration

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

from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView
from crams_log import views
# from merc_common import urls as merc_urls


router = routers.SimpleRouter()
router.register(r'login', views.CramsLoginLogViewSet)
# router.register(r'event_log', views.EventLogViewSet)

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
    # path('crams/', include(merc_urls))
]
