from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from mixer.backend.django import mixer

from crams.utils.crams_utils import get_random_string
from crams.test_utils import CommonBaseTestCase

class UnitTestCase(CommonBaseTestCase):
    def get_storage_request_provision(self, storage_request, provision_id=None):
        if not provision_id:
            provision_id = get_random_string(15)

        return {
            "id": storage_request.id,
            "provision_id": provision_id,
            "message": get_random_string(50),
            "storage_product": self._get_storage_product(storage_request.storage_product)
        }
    
    def get_compute_request_provision(self):
        return None

    def get_provision_id_update_json(self, storage_prod, prov_id):
        return {
            "storage_product": self._get_storage_product(storage_prod),
            "provision_id": prov_id
        }

    def _get_storage_product(self, storage_product):
        return {
                "id": storage_product.id,
                "storage_type": {
                    "id": storage_product.storage_type.id,
                    "storage_type": storage_product.storage_type.storage_type
                },
                "zone": self._get_zone_dict(storage_product.zone),
                "name": storage_product.name,
                "parent_storage_product": storage_product.parent_storage_product
            }

    def _get_zone_dict(self, zone):
        if zone:
            return {
                "id": zone.id,
                "name": zone.name,
                "description": zone.description
            }
        else:
            return None