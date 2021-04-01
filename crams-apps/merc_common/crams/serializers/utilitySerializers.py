# coding=utf-8
"""utilitySerializers."""
import ast

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from rest_framework import serializers, exceptions
from rest_framework.relations import RelatedField
from rest_framework.exceptions import ParseError, ValidationError


class UpdatableSerializer(object):
    """class UpdatableSerializer."""

    def update(self, instance, validated_data):
        """update.

        :param instance:
        :param validated_data:
        :return instance:
        """
        for f in self.model._meta.get_all_field_names():
            setattr(instance, f, validated_data.get(f, getattr(instance, f)))
        instance.save()
        return instance


class CreateOnlyModelSerializer(serializers.ModelSerializer):
    """class ReadOnlyModelSerializer."""

    def update(self, instance, validated_data):
        """update.

        :param instance:
        :param validated_data:
        """
        raise ParseError('Update not allowed ')

    def __delete__(self, instance):
        raise exceptions.APIException('Delete not Allowed')


class UpdateOnlyModelSerializer(serializers.ModelSerializer):
    """class UpdateOnlyModelSerializer."""

    def create(self, validated_data):
        """create.

        :param validated_data:
        """
        raise ParseError('Create not allowed ')

    def __delete__(self, instance):
        raise exceptions.APIException('Delete not Allowed')


class ReadOnlyModelSerializer(UpdateOnlyModelSerializer):
    """class ReadOnlyModelSerializer."""

    def update(self, instance, validated_data):
        """update.

        :param instance:
        :param validated_data:
        """
        raise ParseError('Update not allowed ')


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
                raise ParseError(msg)
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
                raise ParseError('{} is not a dict object', data)
            ret_dict = {}
            for k in self.pkFields:
                try:
                    ret_dict[k] = data_dict[k]
                except Exception:
                    raise ParseError(
                        '{}: Field {} required'.format(self.label, k))
            return ret_dict

        return data

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
                elif value.pk is not None:
                    instance = self.get_queryset().get(pk=value.pk)
                else:
                    return None

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


class DynamicFieldsBaseSerializer(serializers.BaseSerializer):
    """class DynamicFieldsBaseSerializer.

    A BaseSerializer that takes an additional `fields` argument that
    controls which fields should be displayed dynamically at invocation
    """

    def __init__(self, *args, **kwargs):
        """init.

        :param *args:
        :param **kwargs:
        """
        # Don't pass the 'fields' arg up to the superclass
        self.displayFields = kwargs.pop('display', None)
        self.validateRequired = kwargs.pop('required', None)
        # Instantiate the superclass normally
        super(DynamicFieldsBaseSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, obj):
        """to representation.

        :param obj:
        :param ret_dict:
        """
        ret_dict = {}
        if self.displayFields:
            for k in self.displayFields:
                ret_dict[k] = getattr(obj, k)

        return ret_dict

    def to_internal_value(self, data):
        """to internal value.

        :param data:
        :param ret_dict:
        """
        ret_dict = {}
        required = self.validateRequired
        if not required:
            required = ['id']
        for k in required:
            # Perform the data validation.
            val = data.get(k, None)
            if not val:
                raise ValidationError({
                    k: 'This field is required.'
                })
            ret_dict[k] = val

        return ret_dict


# refactored From http://tinyurl.com/ohsgt4g
class DynamicLookupModelSerializer(ReadOnlyModelSerializer):
    """class DynamicLookupModelSerializer.

    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    class Meta(object):
        pass

    def __init__(self, *args, **kwargs):
        """init.

        :param *args:
        :param **kwargs:
        """
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)
        # make sure this is a model class, not a string
        model = kwargs.pop('model', None)
        self.validateRequired = kwargs.pop('required', None)

        if model:
            self.Meta.model = model

        # Instantiate the superclass normally
        super(DynamicLookupModelSerializer, self).__init__(*args, **kwargs)

        if fields:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_internal_value(self, data):
        """to internal value.

        :param data:
        :return ret_dict:
        """
        ret_dict = {}
        required = self.validateRequired
        if not required:
            required = ['id']
        for k in required:
            # Perform the data validation.
            val = data.get(k, None)
            if not val:
                raise ValidationError({
                    k: 'This field is required.'
                })
            ret_dict[k] = val

        return ret_dict

    def to_representation(self, instance):
        """to representation.

        :param instance:
        :return ret_dict:
        """
        ret_dict = {}
        if self.fields:
            for k in self.fields:
                ret_dict[k] = getattr(instance, k)

        return ret_dict


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """class DynamicFieldsModelSerializer.

    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        """init.

        :param *args:
        :param **kwargs:
        """
        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        fields = self.context['request'].query_params.get('fields')
        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProjectAdminField(RelatedField):
    """class ProjectAdminField."""

    def to_representation(self, value):
        """to representation.

        :param value:
        :return dict:
        """
        ret_list = []
        for id in value.project_ids.all():
            ret_list.append({'system': id.system.key, 'id': id.identifier})

        return {'title': value.title, 'ids': ret_list, 'id': value.id}
