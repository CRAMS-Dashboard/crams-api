import pytest
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer

from crams_storage.models import StorageProduct, StorageType
from crams_allocation.models import FundingBody, Provider
from crams.models import Zone

from datetime import datetime


class TestStorageProduct(TestCase):
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

    def test_storage_product(self):
        assert self.storage_prod_result.name == 'Volume (Monash)'
        assert self.storage_prod_result.storage_type.storage_type == 'Volume'
        assert self.storage_prod_result.provider.name == 'Monash'
        assert self.storage_prod_result.funding_body.name == 'Monash'
