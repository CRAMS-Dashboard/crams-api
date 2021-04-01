from mixer.backend.django import mixer
from rest_framework.reverse import reverse

from crams.models import FORCode
from crams.test_utils import CommonBaseTestCase


class TestLookupView(CommonBaseTestCase):
    def setUp(self):
        self.client = self.non_auth_client()
        # create some forcodes for testing
        mixer.blend(FORCode, code='0001', description='FORCode 1')
        mixer.blend(FORCode, code='0002', description='FORCode 2')
        mixer.blend(FORCode, code='0003', description='FORCode 3')

    def test_forcode_view(self):
        forcode_url = reverse("for_codes")
        response = self.client.get(forcode_url)
        assert response.status_code == 200
        # there should be some for codes already setup
        # this test will check only the ones created in the test setup()
        test_forcodes = ['0001 FORCode 1', '0002 FORCode 2', '0003 FORCode 3']
        test_forcodes_found = 0
        for forcode in response.data:
            if forcode['desc'] in test_forcodes:
                test_forcodes_found += 1
        if test_forcodes_found == len(test_forcodes):
            assert True
        else:
            assert False
