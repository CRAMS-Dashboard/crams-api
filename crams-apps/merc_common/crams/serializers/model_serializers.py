# coding=utf-8
"""model related serializers"""

import ast

from rest_framework import serializers, exceptions as rest_exceptions
from django.core.exceptions import ObjectDoesNotExist
# from django.core.exceptions import ValidationError as django_ValidationError
from django.db import models, transaction

from crams import models as crams_models
# from crams import permissions
from crams.utils import debug, rest_utils
# from crams.constants import code


# class HasPermissionModelSerializer(serializers.Serializer):
#     def validate(self, attrs):
#         suffix_msg = ' required to determine save access'
#
#         error_message = '"context" object not found,' + suffix_msg
#         if not self.context or 'request' not in self.context:
#             raise Exception(error_message)
#
#         # if code.USER_HAS_SAVE_PROJECT_ACCESS not in self.context:
#         #     project = attrs.get('project')
#         #     if not project:
#         #         request = attrs.get('request')
#         #         if not request:
#         #             raise Exception(
#         #                 'Unable to identify associated Project ' + suffix_msg)
#         #         project = request.project
#         #
#         #         self.context[code.USER_HAS_SAVE_PROJECT_ACCESS] = \
#         #             permissions.has_save_access_to_project(
#         #                 project, self.context.request.user)
#         #
#         # no_access_msg = 'User does not have save access to associated Project'
#         # if not self.context[code.USER_HAS_SAVE_PROJECT_ACCESS]:
#         #     raise Exception(no_access_msg)
#
#         return attrs
#
#
# class CreateOnlySerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#
#     def update(self, instance, validated_data):
#         raise rest_exceptions.ParseError('Update not allowed ')
#
#     def create(self, validated_data):
#         raise rest_exceptions.ParseError('create Not implemented yet ')


class CreateOnlyModelSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    def update(self, instance, validated_data):
        """update.

        :param instance:
        :param validated_data:
        """
        raise rest_exceptions.ParseError('Update not allowed ')

    def __delete__(self, instance):
        raise rest_exceptions.APIException('Delete not Allowed')

    def get_current_user(self):
        user, context = rest_utils.get_current_user_from_context(self)
        return user

    @classmethod
    def add_related_entities(
            cls, validated_data, related_tables_map, parent_set_callback_fn):
        for key, model in related_tables_map.items():
            data = validated_data.get(key)
            if data:
                for instance_data in data:
                    instance = model(**instance_data)
                    parent_set_callback_fn(instance)
                    instance.save()


class ReadOnlyModelSerializer(CreateOnlyModelSerializer):
    def create(self, validated_data):
        """
        create
        :param validated_data:
        :return:
        """
        raise rest_exceptions.ParseError('Create not allowed ')


class PrimaryKeyLookupField(serializers.PrimaryKeyRelatedField):
    """class PrimaryKeyLookupField.
        - cannot be used for optional serializer fields
    """

    def __init__(self, *args, **kwargs):
        """init.

        :param *args:
        :param **kwargs:
        """
        # Don't pass the 'fields' arg up to the superclass
        # Grant._meta.get_all_field_names()
        self.fields = kwargs.pop('fields', ['id'])
        self.pkFields = kwargs.pop('keyFields', ['id'])
        self.model = None

        # make sure this is a model class, not a string
        model = kwargs.pop('model', None)
        if model:
            msg = '{} is not an instance of django Model'.format(model)
            if not isinstance(model(), models.Model):
                raise rest_exceptions.ParseError(msg)
            self.model = model

        # Instantiate the superclass normally
        super(PrimaryKeyLookupField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        """to internal value.

        :param data:
        :return data:
        """
        if len(self.pkFields) > 0:
            data_dict = data
            if isinstance(data_dict, str):
                data_dict = ast.literal_eval(data)
            if not isinstance(data_dict, dict):
                msg = '{} is not a dict object'
                raise rest_exceptions.ParseError(msg, data)
            ret_dict = {}
            for k in self.pkFields:
                try:
                    ret_dict[k] = data_dict[k]
                except Exception:
                    raise rest_exceptions.ParseError(
                        '{}: Field {} required'.format(self.label, k))
            return self.get_queryset().get(**ret_dict)

        return super().to_internal_value(data)

    def to_representation(self, value):
        """to representation.

        :param value:
        :return ret_dict:
        """
        if self.pk_field is not None:
            return self.pk_field.to_representation(value.pk)

        try:
            if self.model:
                instance = self.model.objects.get(pk=value.pk)
            else:
                if isinstance(value, dict):
                    instance = self.get_queryset().get(**value)
                else:
                    instance = self.get_queryset().get(pk=value.pk)

            ret_dict = {}
            if self.fields:
                for k in self.fields:
                    if isinstance(k, dict):
                        for name, path in k.items():
                            node = instance
                            for attr in path.split('.'):
                                node = getattr(node, attr)
                            ret_dict[name] = node
                    else:
                        ret_dict[k] = getattr(instance, k)
            return ret_dict

        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=value.pk)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(value.pk).__name__)


class ModelLookupSerializer(serializers.Serializer, debug.Debug):
    IGNORE_NOT_EXIST = 'ignore_not_exist'

    def get_model_name(self):
        model_name = None
        if hasattr(self, 'Meta'):
            model_name = self.Meta.model.__name__
        return model_name

    def verify_field_value(self, field_name, attrs, ignore_case=False):
        if self.instance and field_name in attrs:
            field_value = attrs.get(field_name)
            msg = 'value for {} does not match {} with id {}'
            attr_value = getattr(self.instance, field_name)
            if ignore_case:
                field_value = field_value.lower()
                attr_value = attr_value.lower()
            if not field_value == attr_value:
                model_name = self.get_model_name()
                raise rest_exceptions.ValidationError(
                    msg.format(field_name, model_name, self.instance.id))

    def validate(self, attrs):
        if hasattr(self, 'Meta'):
            pk_dict = dict()
            pk_found = False
            if 'id' in attrs:
                pk = attrs.pop('id')
                if pk:
                    pk_dict['id'] = pk
                    pk_found = True
            else:
                if hasattr(self.Meta, 'pk_fields'):
                    pk_found = True
                    for pk_field in self.Meta.pk_fields:
                        if pk_field not in attrs:
                            pk_found = False
                            break
                        pk_dict[pk_field] = attrs.get(pk_field)

            if pk_found:
                if isinstance(self.Meta.model, crams_models.ArchivableModel):
                    if 'archive_ts__isnull' not in pk_dict:
                        pk_dict['archive_ts__isnull'] = True
                try:
                    self.instance = self.Meta.model.objects.get(**pk_dict)
                    invalid_fields = list()
                    for k, v in attrs.items():
                        if not hasattr(self.instance, k):
                            invalid_fields.append(k)

                    if invalid_fields:
                        raise rest_exceptions.ValidationError(
                            'Fields {} invalid for model {}'.format(
                                invalid_fields, self.Meta.model.__name__))

                except self.Meta.model.DoesNotExist:
                    if 'id' not in pk_dict and hasattr(self.Meta, 'flags'):
                        if self.IGNORE_NOT_EXIST in self.Meta.flags:
                            pass
                    else:
                        msg = '{} does not exist for {}'
                        raise rest_exceptions.ValidationError(
                            msg.format(self.Meta.model.__name__, pk_dict))
        return attrs

    def create(self, validated_data):
        msg = 'Create not allowed for {}'.format(self.get_model_name())
        raise rest_exceptions.ValidationError(msg)

    def update(self, instance, validated_data):
        msg = 'Update not allowed for {}'.format(self.get_model_name())
        raise rest_exceptions.ValidationError(msg)


class CreateModelLookupSerializer(ModelLookupSerializer):
    def update_related(self, instance, validated_data):
        error_dict = dict()
        update_nested = list()
        if hasattr(self.Meta, 'update_nested'):
            update_nested = self.Meta.update_nested

        for related_field in self.Meta.related_fk:
            if related_field not in validated_data:
                continue
            validated_data.pop(related_field)
            sz = self.fields.get(related_field)
            msg = 'Serializer not found for {}'.format(related_field)
            if not sz:
                raise rest_exceptions.ValidationError(msg)

            if related_field not in update_nested:
                validated_data[related_field] = sz.instance
                continue

            # update Nested relation data, if required
            related_data_initial = self.initial_data.get(related_field)
            new_sz = type(sz)(instance=sz.instance, data=related_data_initial)
            new_sz.is_valid(raise_exception=True)
            new_sz.save()
            validated_data[related_field] = new_sz.instance

        if error_dict:
            raise rest_exceptions.ValidationError(error_dict)

        return instance

    @classmethod
    def model_validate_save(cls, model_instance_obj):
        model_name = model_instance_obj._meta.model_name
        try:
            model_instance_obj.validate_unique()
            model_instance_obj.save()
        except django_ValidationError as e:
            msg = ','.join(e.messages)
            raise rest_exceptions.ValidationError({model_name: msg})
        except Exception as e:
            raise rest_exceptions.ValidationError({model_name: str(e)})

    def validate(self, data):
        data = super().validate(data)
        if self.instance:
            return data
        msg_base = 'field is required'
        err_dict = dict()
        for required in self.Meta.required_at_save:
            if required not in data:
                err_dict[required] = msg_base.format(required)
        if err_dict:
            raise rest_exceptions.ValidationError(err_dict)

        return data

    def save_common(self, instance, validated_data):
        # create related fields
        many_to_many_dict = dict()
        if hasattr(self.Meta, 'many_to_many'):
            base_msg = 'Many to Many field {} not found for {}'
            for many_field in self.Meta.many_to_many:
                msg = base_msg.format(many_field, self.Meta.model)
                if not hasattr(self.Meta.model, many_field):
                    raise rest_exceptions.ValidationError(msg)
                if many_field not in validated_data:
                    continue
                many_data_list = validated_data.pop(many_field)
                if many_data_list:
                    many_to_many_dict[many_field] = set(many_data_list)

        reverse_dict = dict()
        if hasattr(self.Meta, 'reverse_fk'):
            for (reverse_field, instance_field) in self.Meta.reverse_fk:
                if reverse_field not in validated_data:
                    continue
                field_validated_list = validated_data.pop(reverse_field)
                if not field_validated_list:
                    continue

                reverse_sz = self.fields.get(reverse_field)
                error_list = list()
                msg = 'Serialzer not found for {}'.format(reverse_field)
                if not reverse_sz:
                    error_list.append(msg)
                else:
                    msg = 'reverse serializer'
                    list_msg = msg + ' is not a list serializer'
                    if not reverse_sz.child:
                        error_list.append(list_msg)
                if error_list:
                    raise rest_exceptions.ValidationError({
                        reverse_field: error_list
                    })

                sz_class = type(reverse_sz.child)
                reverse_field_sz_list = list()
                for reverse_data in self.initial_data.get(reverse_field):
                    sz = sz_class(data=reverse_data)
                    sz.is_valid(raise_exception=True)
                    reverse_field_sz_list.append(sz)
                reverse_dict[reverse_field] = \
                    (reverse_field_sz_list, instance_field)

        if hasattr(self.Meta, 'related_fk'):
            self.update_related(instance, validated_data)

        if instance or self.instance:
            if not instance:
                instance = self.instance
            for k, v in validated_data.items():
                setattr(instance, k, v)
        else:
            instance = self.Meta.model(**validated_data)
        self.model_validate_save(instance)

        if reverse_dict:
            error_list = list()
            update_sz_list = list()
            for reverse_field, val in reverse_dict.items():
                (reverse_field_sz_list, instance_field) = val
                for sz in reverse_field_sz_list:
                    if sz.instance:
                        existing = getattr(sz.instance, instance_field)
                        if not existing == instance:
                            msg = 'Cannot change reverse parent for id'
                            error_list.append(msg.format(reverse_sz.instance))
                if error_list:
                    raise rest_exceptions.ValidationError({
                        reverse_field: error_list
                    })
                else:
                    sz.validated_data[instance_field] = instance
                    update_sz_list.append(sz)

            for sz in update_sz_list:
                if sz.instance:
                    changed = False
                    for k, v in sz.validated_data.items():
                        e_v = getattr(sz.instance, k)
                        if not v == e_v:
                            setattr(sz.instance, k, v)
                            changed = True
                    if changed:
                        sz.instance.save()
                    continue
                reverse_obj = sz.Meta.model(**sz.validated_data)
                self.model_validate_save(reverse_obj)

        if many_to_many_dict:
            error_dict = dict()
            for many_field, many_field_set in many_to_many_dict.items():
                try:
                    setattr(instance, many_field, many_field_set)
                except Exception as e:
                    error_dict[many_field] = str(e)
            if error_dict:
                raise rest_exceptions.ValidationError(error_dict)

        return instance

    @transaction.atomic()
    def create(self, validated_data):
        return self.save_common(None, validated_data)

    @transaction.atomic()
    def update(self, instance, validated_data):
        raise rest_exceptions.ValidationError('Update Not Implemented Yet')


class RelatedModelLookupSerializer(ModelLookupSerializer):
    pass


class UpdateModelLookupSerializer(CreateModelLookupSerializer):
    @transaction.atomic()
    def update(self, instance, validated_data):
        return self.save_common(instance, validated_data)
