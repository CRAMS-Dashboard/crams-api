"""crams_collection URL Configuration

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
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views

from django.contrib import admin
from rest_framework import routers

from crams_allocation.viewsets.list_request import AllocationListViewset
from crams_allocation.viewsets.list_request import ProjectRequestListViewSet
from crams_allocation.viewsets.allocation_exists import AllocationExistsViewset
from crams_allocation.viewsets.allocation_viewsets import ProjectRequestViewSet
from crams_allocation.viewsets.project_request_contact import AdminProjectRequestContactViewSet
from crams_allocation.views.project_request_list import EResearchAllocationsCounter
from crams_allocation.views.approve_request_list import ApproveRequestListView
# from crams_allocation.views.provision_request_list import ProvisionRequestListView
from crams_allocation.views.request_history import RequestHistoryViewSet
# from crams_allocation.views.lookup_api import fb_storage_product
# from crams_allocation.viewsets.provision_request import ProvisionProjectViewSet
from crams_allocation.viewsets.decline_request import DeclineRequestViewSet
from crams_allocation.viewsets.approve_request import ApproveRequestViewSet


router = routers.SimpleRouter()
router.register(r'exists', AllocationExistsViewset, basename='project')
router.register(r'request_history', RequestHistoryViewSet, basename='history')
router.register(r'admin/contact', AdminProjectRequestContactViewSet)
router.register(r'allocation_list', AllocationListViewset)
router.register(r'project_request_list', ProjectRequestListViewSet, basename='project-request-list')
router.register(r'project_request', ProjectRequestViewSet, basename='project-request')
# router.register(r'provision', ProvisionProjectViewSet)
router.register(r'decline_request', DeclineRequestViewSet, basename='decline-request')
router.register(r'approve_request', ApproveRequestViewSet, basename='approve-request')


urlpatterns = [
    path('', include(router.urls)),
    # path('admin/', admin.site.urls),
    path('accounts/login', auth_views.LoginView.as_view()),
    # re_path(r'storage_products/(?P<fb_name>[-\w]+)', fb_storage_product, name='storage_products'),
    # allocation urls
    path(r'alloc_counter', EResearchAllocationsCounter.as_view()),
    path(r'approve_list', ApproveRequestListView.as_view()),
    # path(r'provision_list', ProvisionRequestListView.as_view()),

]
