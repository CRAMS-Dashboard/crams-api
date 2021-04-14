from django.conf.urls import url, include
from rest_framework import routers

from crams_provision.viewsets.allocation_provision import RequestProvisionViewSet
from crams_provision.viewsets.allocation_provision import StorageRequestProvisionViewSet
from crams_provision.viewsets.allocation_provision import ComputeRequestProvisionViewSet
# from crams_provision.viewsets.contact_id_provision import ContactProvisionViewSet
from crams_provision.viewsets.project_id_provision import ProjectIDProvisionViewSet

from crams_provision.viewsets.manual_project_request_provision import ProvisionProjectViewSet
from crams_provision.viewsets.manual_project_request_provision import ProvisionRequestViewSet

router = routers.SimpleRouter(trailing_slash=True)
# router.register(r'provision/provision_users', ContactProvisionViewSet)
router.register(r'provision/project_ids', ProjectIDProvisionViewSet)
router.register(r'provision/requests', RequestProvisionViewSet)
router.register(r'provision/storage_requests', StorageRequestProvisionViewSet)
router.register(r'provision/compute_requests', ComputeRequestProvisionViewSet)

router.register(r'provision_project/list', ProvisionProjectViewSet)
router.register(r'provision_request/list', ProvisionRequestViewSet)

urlpatterns = [
    url(r'^', include((router.urls, 'provision'), namespace='provision')),
]
