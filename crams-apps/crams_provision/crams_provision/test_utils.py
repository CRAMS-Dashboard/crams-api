from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from mixer.backend.django import mixer

from crams.utils.crams_utils import get_random_string
from crams.test_utils import CommonBaseTestCase

class UnitTestCase(CommonBaseTestCase):
    def get_request_dict(self, request):
        return {
            "id": request.id,
            "compute_requests": [],
            "storage_requests": [],
            "sent_email": False
        }
    
    def get_storage_request_dict(self, sp_req, provision_id=None):
        if not provision_id:
            provision_id = get_random_string(15)

        return {
            "id": sp_req.id,
            "provision_id": provision_id,
            "success": True,
            "message": "",
            "storage_product": {
                "id": sp_req.storage_product.id,
                "storage_type": {
                    "id": sp_req.storage_product.storage_type.id,
                    "storage_type": sp_req.storage_product.storage_type.storage_type
                },
                "zone": self.get_zone_dict(sp_req.storage_product.zone),
                "name": sp_req.storage_product.name,
                "parent_storage_product": sp_req.storage_product.parent_storage_product
            }
        }
    
    def get_compute_request_dict(self):
        return None

    def get_zone_dict(self, zone):
        if zone:
            return {
                "id": zone.id,
                "name": zone.name,
                "description": zone.description
            }
        else:
            return None
    
    def get_provision_json_payload(self, project, provision_id=None):
        request_list = list()
        for req in project.requests.all():
            req_dict = self.get_request_dict(req)
            
            sp_req_list = list()
            for sp_req in req.storage_requests.all():
                sp_req_dict = self.get_storage_request_dict(sp_req)
                sp_req_list.append(sp_req_dict)

            req_dict["storage_requests"] = sp_req_list
            request_list.append(req_dict)
        
        return {
            "id": project.id,
            "success": True,
            "message": "Provision message",
            "project_ids": [],
            "requests": request_list
        }