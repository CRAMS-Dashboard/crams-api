"""
 crams api URL Configuration
"""

from crams_allocation import urls as allocation_urls
from crams_collection import crams_api_urls as collection_urls
from crams_contact import crams_api_urls as contact_urls
from crams_provision import urls as provision_urls
# from crams_resource_usage import urls as resource_usage_urls
from crams_member import urls as member_urls
from crams_storage import urls as storage_urls
from crams_reports import urls as report_urls
from django.contrib import admin
from django.urls import path, include
from merc_common import urls as common_urls
from rest_framework import routers
from crams_notification import urls as notification_urls
from crams_compute import urls as compute_urls

router = routers.SimpleRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('', include(contact_urls)),
    path('', include(provision_urls)),
    path('', include(allocation_urls)),
    path('', include(collection_urls)),
    path('member/', include(member_urls)),
    path('', include(storage_urls)),
    path('reports/', include(report_urls)),
    path('', include(common_urls)),
    path('', include(notification_urls)),
    path('', include(compute_urls)),
]
