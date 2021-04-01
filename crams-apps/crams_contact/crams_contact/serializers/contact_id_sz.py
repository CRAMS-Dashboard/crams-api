# coding=utf-8
"""

"""
import copy
from rest_framework import serializers, exceptions

from crams.serializers import erb_serializers
from crams_contact.utils import contact_utils
from crams_contact import models as contact_models
from crams_contact.serializers import util_sz
from crams_contact.serializers.role_free_contact_serializer import RoleFreeContactSerializer


class ContactIDSerializer(erb_serializers.BaseIdentifierSerializer):
    class Meta(object):
        """meta Class."""

        model = contact_models.EResearchContactIdentifier
        fields = ('identifier', 'system')

    @classmethod
    def build_contact_id_list_json(
            cls, contact_id_obj_list, json_id_key='contact_ids'):
        def build_json(contact_obj, pk_list):
            sz = cls(pk_list, many=True)
            return {
                'id': contact_obj.id,
                'given_name': contact_obj.given_name,
                'surname': contact_obj.surname,
                'email': contact_obj.email,
                json_id_key: sz.data
            }

        contact_dict = dict()
        for cid in contact_id_obj_list:
            id_list = contact_dict.get(cid.contact)
            if not id_list:
                id_list = list()
                contact_dict[cid.contact] = id_list
            id_list.append(cid)

        ret_list = list()
        for contact, id_list in contact_dict.items():
            ret_list.append(build_json(contact, id_list))
        return ret_list

    @classmethod
    def update_contact_data_list(cls, id_key, contact_data_list):
        contact_id_obj_list = list()
        for contact_data in contact_data_list:
            for sz in contact_data.get(id_key, list()):
                contact_id_obj_list.append(sz.save())

        return contact_id_obj_list

    @classmethod
    def validate_contact_identifiers_in_contact_list(cls, contact_data_list, current_user, id_key='contact_ids'):
        def build_contact_error(contact_data_to_copy, err_message, errors=None):
            err_dict = copy.copy(contact_data_to_copy)
            err_dict.pop('contact_obj', None)
            err_dict['error'] = True
            err_dict['error_message'] = err_message
            if errors:
                err_dict[id_key] = errors
            return err_dict
        role_fn = contact_utils.fetch_erb_userroles_with_provision_privileges
        user_erb_roles = role_fn(current_user)
        err_list = list()
        for contact_data in contact_data_list:
            contact_ids = contact_data.pop(id_key, list())
            contact = RoleFreeContactSerializer.fetch_first_contact_obj(contact_data)
            if not contact:
                msg = 'Contact not found'
                err_list.append(build_contact_error(contact_data, msg))
                continue

            contact_data['contact_obj'] = contact
            id_err_list = list()
            contact_id_sz_list = list()
            contact_data[id_key] = contact_id_sz_list
            context = {
                'contact': contact,
                'user_erb_roles': user_erb_roles,
                'current_user': current_user
            }
            for sid in contact_ids:
                sz = cls(data=sid, context=context)
                sz.is_valid(raise_exception=False)
                if sz.errors:
                    sid['error_message'] = sz.errors
                    id_err_list.append(sid)
                    continue
                contact_id_sz_list.append(sz)

            if id_err_list:
                msg = 'Error processing Contact Ids'
                err_list.append(build_contact_error(
                    contact_data, msg, id_err_list))

        if err_list:
            raise exceptions.ValidationError(err_list)

        return contact_data_list

    def validate_contact(self, validated_data):
        contact = validated_data.get('contact')
        if not contact or not isinstance(contact, contact_models.Contact):
            msg = 'Contact object must be passed in context'
            raise exceptions.ValidationError(msg)

        self.instance = self.fetch_identifier_unique_for_system(
            validated_data, model=contact_models.EResearchContactIdentifier)

    def validate(self, data):
        validated_data = dict()
        validated_data['system'] = data.get('system')
        validated_data['parent_erb_contact_id'] = None

        contact = self.context.get('contact')
        if contact and isinstance(contact, contact_models.Contact):
            validated_data['contact'] = contact
            self.validate_contact(validated_data)

        validated_data['identifier'] = data.get('identifier')
        return validated_data

    def create(self, validated_data):
        self.validate_contact(validated_data)
        if self.instance:
            return self.update(self.instance, validated_data)
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        new_instance = self.Meta.model.objects.create(**validated_data)

        # Archive previous value for identifier
        instance.parent_erb_contact_id = new_instance
        instance.save()

        # Update archived objects parent_id with latest Identifier object
        qs = contact_models.EResearchContactIdentifier.objects.filter(
            parent_erb_contact_id=instance)
        if qs.exists():
            for cid in qs.all():
                cid.parent_erb_contact_id = new_instance
                cid.save()

        return new_instance


class ContactSystemIdentifierSz(util_sz.EmptySerializer):
    class ContactIdExImSerializer(util_sz.EmptySerializer):
        class SystemId(util_sz.EmptySerializer):
            key = serializers.CharField()
            e_research_body = serializers.CharField()

        system = SystemId()
        identifier = serializers.CharField()

    system_identifiers = serializers.SerializerMethodField()
    first_name = serializers.CharField(source='given_name', required=False)
    last_name = serializers.CharField(source='surname', required=False)
    email = serializers.EmailField()
    id = serializers.IntegerField(required=False)

    def get_system_identifiers(self, contact_obj):
        id_list = contact_obj.system_identifiers
        valid_erb_list = self.context.get('valid_erb_list', None)
        if not valid_erb_list:
            return self.ContactIdExImSerializer(id_list, many=True).data

        ret_list = list()
        for erb_contact_id_obj in id_list:
            if erb_contact_id_obj.system.e_research_body in valid_erb_list:
                ret_list.append(self.ContactIdExImSerializer(erb_contact_id_obj).data)
        return ret_list

    class Meta(object):
        fields = ('id', 'first_name', 'last_name',
                  'email', 'system_identifiers')
        read_only_fields = ('first_name', 'last_name', 'id')
