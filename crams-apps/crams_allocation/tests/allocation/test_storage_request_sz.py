import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from crams_storage.models import StorageProduct, StorageType
from crams_allocation.models import FundingBody, Provider
from crams.models import Zone
from crams_allocation.product_allocation.models import StorageRequest
from crams_allocation.product_allocation.serializers.storage_request_serializers import StorageRequestSerializer
from datetime import datetime


class TestStorageRequestSerializer(TestCase):
    def setUp(self):
        creation_ts = datetime.now()
        last_modified_ts = datetime.now()
        start_date = datetime.now().date()
        provider = mixer.blend(Provider, name='Monash', active=True, creation_ts=creation_ts,
                               description='Monash storage provider', last_modified_ts=last_modified_ts,
                               start_date=start_date)

        funding_body = mixer.blend(FundingBody, name='Monash', email='crams@rc.test.nectar.org.au')
        zone = mixer.blend(Zone, name='monash', description='Monash (VIC)')
        storage_type = mixer.blend(StorageType, storage_type='Volume')

        storage_product = mixer.blend(StorageProduct, name='Volume (Monash)',
                                      funding_body=funding_body,
                                      provider=provider,
                                      storage_type=storage_type,
                                      zone=zone)

        self.storage_prod_result = StorageProduct.objects.last()

    def test_storage_request_serializer_validation(self):
        sp_req_json_data = {
            "current_quota": 0,
            "requested_quota_change": 20,
            "requested_quota_total": 20,
            "approved_quota_change": 0,
            "approved_quota_total": 0,
            "storage_product": {
                "id": self.storage_prod_result.id,
                "name": "Volume (Monash)"
            },
            "storage_question_responses": [],
        }
        sz = StorageRequestSerializer(data=sp_req_json_data)

        assert sz.is_valid()
        sz.validated_data['requested_quota_change'] == 20
        # sz.save()
        storage_product = sz.validated_data.pop('storage_product')
        assert storage_product.name == 'Volume (Monash)'
