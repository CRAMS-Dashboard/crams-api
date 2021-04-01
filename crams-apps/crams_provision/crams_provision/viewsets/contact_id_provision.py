# # coding=utf-8
# """
#
# """
#
# from crams.permissions import IsCramsAuthenticated
# from crams.models import ProvisionDetails
# from crams_collection.models import Project
# from crams_contact.models import Contact, EResearchContactIdentifier
# from django.db.models import Q
# from rest_framework import decorators, exceptions
# from rest_framework import status
# from rest_framework.response import Response
#
# from crams_provision.serializers import projectid_contact_provision
# from crams_provision.serializers import user_id_provision
# from crams_provision.viewsets.base import ProvisionCommonViewSet
#
#
# class ContactProvisionViewSet(ProvisionCommonViewSet):
#     permission_classes = [IsCramsAuthenticated]
#     queryset = EResearchContactIdentifier.objects.none()
#     serializer_class = user_id_provision.ProvisionContactIDSerializer
#
#     @classmethod
#     def get_queryset(cls):
#         required_status = ProvisionDetails.SET_OF_SENT
#         qs_filter = Q(provision_details__isnull=True) | Q(
#             provision_details__status__in=required_status)
#         qs_filter &= Q(parent_erb_contact_id__isnull=True)
#         return EResearchContactIdentifier.objects.filter(qs_filter)
#
#     @classmethod
#     def build_provision_contact_list(cls, valid_erb_list, project=None):
#         qs = cls.get_queryset().filter(
#             system__e_research_body__in=valid_erb_list)
#         if isinstance(project, Project):
#             qs = qs.filter(contact__project_contacts__project=project)
#         return cls.serializer_class.build_contact_id_list_json(qs.distinct())
#
#     def list(self, request, *args, **kwargs):
#         erb_obj = self.fetch_e_research_body_param_obj()
#
#         valid_erb_list = self.get_user_provision_erbs(
#             self.get_current_user(), erb_obj)
#         if valid_erb_list:
#             return Response(self.build_provision_contact_list(valid_erb_list))
#
#         msg = 'User does not have required Provider privileges'
#         if erb_obj:
#             msg = msg + ' for {}'.format(erb_obj.name)
#         raise exceptions.ValidationError(msg)
#
#     def retrieve(self, request, *args, **kwargs):
#         e_research_body = self.request.query_params.get(
#             'e_research_body', None)
#
#         if e_research_body:
#             contact = Contact.objects.get(pk=kwargs["pk"])
#             if contact.system_identifiers.filter(
#                     system__e_research_body__name=e_research_body).exists():
#                 serialize_data = projectid_contact_provision. \
#                     ContactIDProvisionSerializer(contact).data
#                 return Response(serialize_data)
#             else:
#                 # return empty
#                 return Response({"detail": "No contact ids for ERB"},
#                                 status=status.HTTP_200_OK)
#         else:
#             contact = Contact.objects.get(pk=kwargs["pk"])
#             serialize_data = projectid_contact_provision. \
#                 ContactIDProvisionSerializer(contact).data
#             return Response(serialize_data)
#
#     # @decorators.list_route(methods=['post'], url_path='(?P<pk>\d+)/create')
#     def create_user_provision(self, request, *args, **kwargs):
#         # get contact
#         contact = Contact.objects.get(pk=kwargs['pk'])
#
#         # ignore the contact obj changes, focus on changes in contact_ids
#         err_cnt_ids = []
#
#         # create the eresearch contact identifier for user
#         for req_cnt_id in request.data['contact_ids']:
#             try:
#                 contact_id = EResearchContactIdentifier()
#                 contact_id.contact = contact
#                 contact_id.identifier = req_cnt_id['identifier']
#                 contact_id.system_id = req_cnt_id['system']['id']
#                 contact_id.provisioned = True
#                 contact_id.save()
#
#             except:
#                 # unable to save contact id
#                 err_cnt_ids.append(req_cnt_id['identifier'])
#
#         # display error message
#         if err_cnt_ids:
#             return Response(
#                 "Error creating contact_ids, the following"
#                 " ids were not updated: " + str(err_cnt_ids),
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         serialize_data = projectid_contact_provision. \
#             ContactIDProvisionSerializer(contact).data
#
#         return Response(serialize_data)
#
#     @decorators.action(detail=False, methods=['post'], url_path='(?P<pk>\d+)/update')
#     def update_user_provision(self, request, *args, **kwargs):
#         # get contact and contact_ids
#         contact = Contact.objects.get(pk=kwargs['pk'])
#
#         # ignore the contact obj changes, focus on changes in contact_ids
#         err_cnt_ids = []
#
#         for req_cnt_id in request.data['contact_ids']:
#             try:
#                 contact_id = EResearchContactIdentifier.objects.get(
#                     pk=req_cnt_id['id'])
#
#                 if contact_id.identifier != req_cnt_id['identifier']:
#                     # update contact_id
#                     contact_id.identifier = req_cnt_id['identifier']
#                     contact_id.provisioned = False
#                     contact_id.save()
#             except:
#                 # error couldn't find the matching contact_id
#                 err_cnt_ids.append(req_cnt_id['identifier'])
#
#         # display error message
#         if err_cnt_ids:
#             return Response(
#                 "Error updating contact_ids, the following"
#                 " ids were not updated: " + str(err_cnt_ids),
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         serialize_data = projectid_contact_provision. \
#             ContactIDProvisionSerializer(contact).data
#
#         return Response(serialize_data)
#
#     @decorators.action(detail=False, methods=['post'], url_path='update')
#     def update_provision(self, request, *args, **kwargs):
#         ret_data = self.update_provision_data_input(
#             request.data, self.get_current_user())
#         return Response(ret_data)
#
#     @classmethod
#     def update_provision_data_input(cls, data, current_user):
#         id_key = 'contact_ids'
#         sz_class = user_id_provision.ProvisionContactIDSerializer
#         sz_fn = sz_class.validate_contact_identifiers_in_contact_list
#         contact_data_list = sz_fn(data, current_user, id_key)
#
#         id_obj_list = sz_class.update_contact_data_list(
#             id_key, contact_data_list)
#
#         return sz_class.build_contact_id_list_json(id_obj_list)
