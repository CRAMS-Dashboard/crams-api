"""
 crams reports URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from crams_reports.viewsets.dashboard import DashboardViewset
from crams_reports.viewsets.storage_usage import ProjectStorageUsageViewset
from crams_reports.viewsets.storage_usage import ProjectStorageUsageHistoryViewset


router = routers.SimpleRouter(trailing_slash=True)
router.register(r'dashboard_project_list', DashboardViewset)
router.register(r'project_storage_product_usage', ProjectStorageUsageViewset)
router.register(r'project_storage_product_usage_history', ProjectStorageUsageHistoryViewset)

urlpatterns = [
    path('', include(router.urls)),
    # path('admin/', admin.site.urls),
]
