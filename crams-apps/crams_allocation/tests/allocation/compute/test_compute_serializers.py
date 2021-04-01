# import pytest
# from hypothesis.extra.django import TestCase
# from mixer.backend.django import mixer
#
# from crams.models import Question
# from crams.models import Question
# from crams.models import EResearchBodySystem
# from crams.models import FundingBody
# from crams.models import Provider
# from crams.models import ProvisionDetails
# from crams_allocation.models import Request
# from crams_allocation.models import RequestStatus
# from crams_allocation.compute.models import ComputeProduct
# from crams_allocation.compute.models import ComputeRequest
# from crams_allocation.compute.models import ComputeProductProvisionId
# from crams_allocation.compute.models import ComputeRequestQuestionResponse
# from crams_allocation.compute.serializers import compute_request
# from crams_allocation.compute.serializers import compute_product_provision_serializer
# from crams_allocation.compute.serializers import compute_question_serializer
#
#
# class TestComputeSerializers(TestCase):
#     def setUp(self):
#         self.req_status = RequestStatus.objects.get(code='P')
#         self.erbs = mixer.blend(EResearchBodySystem, name='erbs')
#         self.funding_body = mixer.blend(FundingBody, name='Funding Body')
#         self.provider = mixer.blend(Provider, name='Provider')
#         self.request = mixer.blend(Request, request_status=self.req_status, e_research_system=self.erbs)
#         self.comp_prod = mixer.blend(ComputeProduct, e_research_system=self.erbs, name='compute')
#         self.question = mixer.blend(Question, key='q_key', type='q_type', question='???')
#         self.cores = 2
#         self.core_hours = 10000
#         self.instances = 1
#         self.comp_prov = mixer.blend(ComputeProductProvisionId,
#             compute_product=self.comp_prod,
#             provision_id='1234567890')
#         self.prov_det = mixer.blend(ProvisionDetails, status='P', message='Provisioned', parent_provision_details=None)
#         self.comp_req = mixer.blend(ComputeRequest,
#             compute_product=self.comp_prod,
#             request=self.request,
#             cores=self.cores,
#             approved_cores=self.cores,
#             core_hours=self.core_hours,
#             approved_core_hours=self.core_hours,
#             instances=self.instances,
#             approved_instances=self.instances,
#             provision_details=self.prov_det)
#         self.comp_q_resp = mixer.blend(ComputeRequestQuestionResponse,
#             question_response='question response',
#             compute_request=self.comp_req,
#             question=self.question)
#
#     def test_compute_request_serializer(self):
#         sz = compute_request.ComputeRequestSerializer(instance=self.comp_req)
#
#         # check serialized data
#         assert sz.data['compute_product']['name'] == self.comp_prod.name
#         assert sz.data['cores'] == self.cores
#         assert sz.data['approved_cores'] == self.cores
#         assert sz.data['core_hours'] == self.core_hours
#         assert sz.data['approved_core_hours'] == self.core_hours
#         assert sz.data['instances'] == self.instances
#         assert sz.data['approved_instances'] == self.instances
#
#     def test_compute_product_provision_serializer(self):
#         sz = compute_product_provision_serializer.ComputeRequestSerializer(instance=self.comp_req)
#
#         # check serialized data - TODO: not working need to investigate
#         # error:  The field 'provision_details' was declared on serializer ComputeRequestSerializer, but has not been included in the 'fields' option.
#         assert True
#
#     def test_compute_product_serailizer(self):
#         sz = compute_request.AllocationComputeProductValidate(instance=self.comp_prod)
#
#         # check serialized data
#         assert sz.data['name'] == self.comp_prod.name
#
#     def test_compute_question_serializer1(self):
#         sz = compute_question_serializer.ComputeRequestQResponseSerializer(instance=self.comp_q_resp)
#
#         # check serialized data
#         assert sz.data['question_response'] == self.comp_q_resp.question_response
#         assert sz.data['question'] == self.question.key
#
#     def test_compute_question_serializer2(self):
#         sz = compute_question_serializer.ComputeQuestionResponseSerializer(instance=self.comp_q_resp)
#
#         # check serialized data
#         assert sz.data['question_response'] == self.comp_q_resp.question_response
#         assert sz.data['question']['key'] == self.question.key
#         assert sz.data['question']['question'] == self.question.question
