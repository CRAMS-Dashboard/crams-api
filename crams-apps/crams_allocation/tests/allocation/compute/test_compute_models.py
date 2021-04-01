# import pytest
# from hypothesis.extra.django import TestCase
# from mixer.backend.django import mixer
#
# from crams.models import Question
# from crams.models import EResearchBodySystem
# from crams.models import FundingBody
# from crams.models import Provider
# from crams_allocation.models import Request
# from crams_allocation.models import RequestStatus
# from crams_allocation.compute.models import ComputeProduct
# from crams_allocation.compute.models import ComputeRequest
# from crams_allocation.compute.models import ComputeProductProvisionId
# from crams_allocation.compute.models import ComputeRequestQuestionResponse
#
#
# class TestComputeModels(TestCase):
#     def setUp(self):
#         self.req_status = RequestStatus.objects.get(code='P')
#         self.erbs = mixer.blend(EResearchBodySystem, name='erbs')
#         self.funding_body = mixer.blend(FundingBody, name='Funding Body')
#         self.provider = mixer.blend(Provider, name='Provider')
#         self.request = mixer.blend(Request, request_status=self.req_status, e_research_system=self.erbs)
#         self.comp_prod = mixer.blend(ComputeProduct, e_research_system=self.erbs, name='compute')
#         self.question = mixer.blend(Question, key='q_key', type='q_type', question='???')
#         self.comp_req = mixer.blend(ComputeRequest, compute_product=self.comp_prod, request=self.request)
#
#     def test_comp_prod_model(self):
#         # create and save model
#         comp_prod = ComputeProduct()
#         comp_prod.e_research_system = self.erbs
#         comp_prod.funding_body = self.funding_body
#         comp_prod.provider = self.provider
#         comp_prod.name = 'new compute'
#         comp_prod.save()
#
#         # fetch saved obj
#         try:
#             saved_comp_prod = ComputeProduct.objects.get(pk=comp_prod.id)
#         except:
#             saved_comp_prod = None
#
#         # check saved values
#         assert saved_comp_prod
#         assert saved_comp_prod.e_research_system == self.erbs
#         assert saved_comp_prod.funding_body == self.funding_body
#         assert saved_comp_prod.provider == self.provider
#         assert saved_comp_prod.name == 'new compute'
#
#     def test_compute_request_model(self):
#         # create and save model
#         comp_req = ComputeRequest()
#         comp_req.request = self.request
#         comp_req.instances = 1
#         comp_req.approved_instances = 1
#         comp_req.cores = 2
#         comp_req.approved_cores = 2
#         comp_req.core_hours = 10000
#         comp_req.approved_core_hours = 10000
#         comp_req.compute_product = self.comp_prod
#         comp_req.save()
#
#         # fetch saved obj
#         try:
#             saved_comp_req = ComputeRequest.objects.get(pk=comp_req.id)
#         except:
#             saved_comp_req = None
#
#         # check saved values
#         assert saved_comp_req
#         assert saved_comp_req.request == self.request
#         assert saved_comp_req.instances == 1
#         assert saved_comp_req.approved_instances == 1
#         assert saved_comp_req.cores == 2
#         assert saved_comp_req.approved_cores == 2
#         assert saved_comp_req.core_hours == 10000
#         assert saved_comp_req.core_hours == 10000
#         assert saved_comp_req.compute_product == self.comp_prod
#
#     def test_comp_prod_prov_id(self):
#         # create and save model
#         comp_prov = ComputeProductProvisionId()
#         comp_prov.compute_product = self.comp_prod
#         comp_prov.provision_id = '1234567890'
#         comp_prov.save()
#
#         # fetch saved obj
#         try:
#             saved_comp_prov = ComputeProductProvisionId.objects.get(pk=comp_prov.id)
#         except:
#             saved_comp_prov = None
#
#         # checked saved values
#         assert saved_comp_prov
#         assert saved_comp_prov.compute_product == self.comp_prod
#         assert saved_comp_prov.provision_id == '1234567890'
#
#     def test_compute_question_response(self):
#         # create and save model
#         comp_q_response = ComputeRequestQuestionResponse()
#         comp_q_response.compute_request = self.comp_req
#         comp_q_response.question = self.question
#         comp_q_response.question_response = 'question response'
#         comp_q_response.save()
#
#         # fetch saved obj
#         try:
#             saved_comp_q_response = ComputeRequestQuestionResponse.objects.get(pk=comp_q_response.id)
#         except:
#             saved_comp_q_response = None
#
#         # check saved values
#         assert saved_comp_q_response
#         assert saved_comp_q_response.compute_request == self.comp_req
#         assert saved_comp_q_response.question == self.question
#         assert saved_comp_q_response.question_response == 'question response'
