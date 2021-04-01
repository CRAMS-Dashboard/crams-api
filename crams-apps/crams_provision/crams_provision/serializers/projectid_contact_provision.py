import logging

from crams.serializers.model_serializers import ReadOnlyModelSerializer
from crams.utils.role import AbstractCramsRoleUtils
from crams_collection.models import ProjectID, Project
from crams_collection.serializers import project_id_serializer
from crams_contact.serializers.contact_id_sz import ContactIDSerializer
from django.contrib import auth
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers, exceptions

from crams_provision.utils import base

LOG = logging.getLogger(__name__)
User = auth.get_user_model()
CLASS_SZ = project_id_serializer.ERBProjectIDSerializer


# class ContactIDProvisionSerializer(ModelLookupSerializer):
#     """class ContactIDProvisionSerializer."""
#
#     id = serializers.SerializerMethodField()
#     given_name = serializers.SerializerMethodField()
#     surname = serializers.SerializerMethodField()
#     email = serializers.SerializerMethodField()
#     organisation = ReadOnlyOrganisationSerializer(many=False, allow_null=True)
#
#     # contact = serializers.SerializerMethodField()
#
#     contact_ids = serializers.SerializerMethodField()
#
#     class Meta(object):
#         model = Contact
#         fields = ('id', 'given_name', 'surname', 'email', 'contact_ids')
#
#     # def get_contact(self, contact_obj):
#     #     return contact_serializers.ContactLookupSerializer(contact_obj).data
#
#     @classmethod
#     def get_id(cls, contact_obj):
#         return contact_obj.id
#
#     @classmethod
#     def get_given_name(cls, contact_obj):
#         return contact_obj.given_name
#
#     @classmethod
#     def get_surname(cls, contact_obj):
#         return contact_obj.surname
#
#     @classmethod
#     def get_email(cls, contact_obj):
#         return contact_obj.email
#
#     def get_current_user(self):
#         return project_user_utils.get_current_user_from_context(self)
#
#     @classmethod
#     def get_contact_ids(cls, contact_obj):
#         ret_ids = []
#         for contact_id in contact_obj.system_identifiers.all():
#             id_dict = OrderedDict()
#             id_dict['id'] = contact_id.id
#             # check contact_id.provision_details
#             # if is not none and status is 'Provisioned' then true, else false
#             if contact_id.provision_details is None:
#                 provision_detail = \
#                     ProvisionDetailUtils.update_or_get_new_provisiondetails_object(
#                         contact_id, False)
#                 provision_detail.save()
#                 contact_id.provision_details = provision_detail
#                 contact_id.save()
#                 id_dict['provisioned'] = False
#             else:
#                 id_dict['provisioned'] = False
#                 if contact_id.provision_details.status == 'Provisioned':
#                     id_dict['provisioned'] = True
#             ret_ids.append(id_dict)
#
#             id_dict['identifier'] = contact_id.identifier
#             id_dict['key'] = contact_id.system.key
#             id_dict['e_research_body'] = contact_id.system.e_research_body.name
#         return ret_ids
#
#     @classmethod
#     def fetch_system_obj(cls, key, erb_name):
#         try:
#             return EResearchBodyIDKey.objects.get(
#                 key=key, e_research_body__name__iexact=erb_name)
#         except EResearchBodyIDKey.DoesNotExist:
#             msg = 'ERB System key not found for {}/{}'
#             raise exceptions.ValidationError(msg.format(key, erb_name))
#
#     def validate_contact_ids(self):
#         if not isinstance(self.instance, Contact):
#             raise exceptions.ValidationError(
#                 'existing instance not Contact object')
#
#         ret_list = list()
#
#         user_erb_roles = \
#             project_user_utils.fetch_erb_userroles_with_provision_privileges(
#                 self.get_current_user())
#         sz_cls = ContactIDSerializer
#         for contact_data in self.initial_data.get('contact_ids'):
#             key = contact_data.get('key')
#             erb_name = contact_data.get('e_research_body')
#             system_obj = self.fetch_system_obj(key, erb_name)
#             contact_data['system'] = {'system_obj': system_obj}
#             obj = sz_cls.fetch_save_object_sz(
#                 contact_data, self.instance, user_erb_roles)
#             if obj:
#                 ret_list.append(obj)
#
#         return ret_list
#
#     def validate(self, data):
#         data['contact_ids'] = self.validate_contact_ids()
#         return data
#
#     @transaction.atomic
#     def update(self, instance, validated_data):
#         erb_contact_list_sz = validated_data.pop('contact_ids', [])
#         ret_contact_system_ids = list()
#         contact_id_objs = list()
#         for sz in erb_contact_list_sz:
#             contact_id_objs.append(sz.save())
#             ret_contact_system_ids.append(sz.data)
#         validated_data['contact_ids'] = ret_contact_system_ids
#         # notify erb_contacts
#         # provisionSerializers.BaseProvisionMessageSerializer.\
#         # send_contact_id_email(contact_id_objs)
#         return instance   # return contact instance to allow proper display


class ProvisionProjectIDUtils(CLASS_SZ, base.BaseProvisionUtils):
    provisioned = serializers.SerializerMethodField()

    class Meta(object):
        """meta Class."""

        model = ProjectID
        fields = ('identifier', 'system', 'provisioned')

    def get_provisioned(self, obj, current_user=None):
        if not current_user:
            current_user = self.get_current_user()
        return self.get_build_provisioned(obj, current_user=current_user)

    @classmethod
    def update_project_data_list(cls, id_key, project_data_list):
        project_id_obj_list = \
            super().update_project_data_list(id_key, project_data_list)

        return project_id_obj_list

    def clone_to_new_project(self, new_project_obj, user_erb_roles):
        if not self.instance:
            msg = 'Cannot clone non-existent project id'
            raise exceptions.ValidationError(msg)
        context = {'CLONE': True,
                   'user_erb_roles': user_erb_roles,
                   'project': self.instance.project,
                   'current_user': self.get_current_user()
                   }
        sz = self.__class__(data=self.data, context=context)
        sz.is_valid(raise_exception=True)
        new_pid = sz.save()
        # update project to new project
        new_pid.project = new_project_obj
        new_pid.save()

    def validate(self, data):
        validated_data = super().validate(data)

        msg_param = 'Project Id'
        provisioned_status = self.initial_data.get('provisioned', False)
        is_clone = 'CLONE' in self.context
        is_admin = AbstractCramsRoleUtils.is_user_erb_admin(self.get_current_user())
        self.validate_provisioned(provisioned_status, self.instance,
                                  msg_param, is_clone, is_admin)
        if self.instance:
            identifier = validated_data.get('identifier')
            if identifier == self.instance.identifier and \
                    not provisioned_status and not is_clone and not is_admin:
                raise exceptions.ValidationError('No change to identifier')
            validated_data['provisioned'] = provisioned_status

        return validated_data

    @transaction.atomic
    def update(self, instance, validated_data):
        new_pd = self.build_new_provision_details(
            instance, validated_data, self.get_current_user())
        new_pd.save()
        validated_data['provision_details'] = new_pd

        new_instance = super().update(instance, validated_data)
        return new_instance


class ProjectMemberContactIDList(ReadOnlyModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta(object):
        """meta Class."""
        model = Project
        fields = ('title', 'members')

    @classmethod
    def build_project_member_json(
            cls, project_obj, valid_erb_list, system_obj=None):
        contact_dict = dict()
        for pc in project_obj.project_contacts.filter(
                contact_role__e_research_body__in=valid_erb_list):
            role_list = contact_dict.get(pc.contact)
            if not role_list:
                role_list = list()
                contact_dict[pc.contact] = role_list
            role_list.append(pc)

        ret_list = []
        for contact, pc_list in contact_dict.items():
            ret_dict = dict()
            ret_list.append(ret_dict)
            ret_dict['contact_ids'] = \
                cls.get_contact_ids(contact, valid_erb_list, system_obj)
            ret_dict['email'] = contact.email
            if pc_list:
                ret_dict['role'] = pc_list[0].contact_role.name

        return ret_list

    @classmethod
    def get_contact_ids(cls, contact_obj, valid_erb_list, system_obj=None):
        ret_ids = list()
        sz_class = ContactIDSerializer
        qs_filter = Q(system__e_research_body__in=valid_erb_list)
        if system_obj:
            qs_filter &= Q(system=system_obj)

        for contact_id in contact_obj.system_identifiers.filter(qs_filter):
            id_dict = sz_class(contact_id).data
            ret_ids.append(id_dict)
        return ret_ids

    def get_members(self, project_obj):
        valid_erb_list = self.context.get('valid_erb_list')
        system_obj = self.context.get('system_obj')
        return self.build_project_member_json(
            project_obj, valid_erb_list, system_obj)
