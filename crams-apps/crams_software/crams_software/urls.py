# coding=utf-8
"""
Report URL definitions
"""

from django.conf.urls import url, include
from rest_framework import routers

from crams_software import views

# Viewset URLs
router = routers.SimpleRouter(trailing_slash=False)
router.register(r'products', views.SoftwareProductList)
router.register(r'license', views.LicenseAgreementViewSet)
router.register(r'contact_license', views.ContactLicenseAgreementViewSet)

urlpatterns = [
    url(r'^', include((router.urls, 'software'), namespace='software')),
    url(r'^category', views.SoftwareProductCategoryList.as_view()),
    url(r'^type', views.SoftwareLicenseTypeList.as_view()),
    url(r'^provision', views.SoftwareProductProvisionList.as_view()),
    url(r'^users/(?P<sw_posix_id>\w+)', views.SoftwareUsersListViewSet.as_view()),
]
