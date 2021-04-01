# coding=utf-8
"""
 validation utils
"""
from abc import ABCMeta

from rest_framework.serializers import ValidationError
from crams.utils.django_utils import get_model_field_value


class ChangedMetadata:
    def __init__(self):
        self.obj_dict = dict()
        self.modified_related_field_set = set()
        self.new_related_field_set = set()
        self.removed_related_field_set = set()
        self.err_list = list()


class FieldsRequiredValidator(metaclass=ABCMeta):
    """class FieldsRequiredValidator."""

    @classmethod
    def get_fields_required(cls):
        """get required fields."""
        return list()

    @classmethod
    def get_fields_unchanged(cls):
        """get fields unchanged"""
        pass

    def __call__(self, obj_dict):
        for field in self.get_fields_required():
            if field not in obj_dict:
                raise ValidationError({field: 'field is required'})


def validate_dry_principle(serializer_instance, fields_unchanged_list,
                           list_name_str, user_role_str):
    """validate dry principle.

    :param serializer_instance:
    :param fields_unchanged_list:
    :param list_name_str:
    :param user_role_str:
    :return: :raise ValidationError:
    """
    if not list_name_str:
        raise ValidationError(
            {'listNameStr / validate_DRY ': 'parameter cannot be null, ' +
                                            'contact Tech Support'})

    if not serializer_instance.instance:
        raise ValidationError({'{}'.format(
            repr(serializer_instance)): 'instance not found, contact ' +
                                        'Tech Support'})

    # Do not use the parsed validatedData, it does not contain id pk
    intial_data_list = serializer_instance.initial_data.get(list_name_str,
                                                            None)
    existing_instance_list = get_model_field_value(
        serializer_instance.instance, list_name_str).all()

    msg = None
    if not intial_data_list:
        if existing_instance_list:
            msg = '{} cannot remove existing {}'.format(
                user_role_str, list_name_str)
    elif not existing_instance_list:
        msg = '{} cannot add new {}'.format(user_role_str, list_name_str)
    elif len(intial_data_list) < len(existing_instance_list):
        msg = '{} cannot remove existing {}'.format(user_role_str,
                                                    list_name_str)
    elif len(intial_data_list) > len(existing_instance_list):
        msg = '{} cannot add new {}'.format(user_role_str,
                                            list_name_str)

    if msg:
        raise ValidationError({list_name_str: msg})

    existing_instance_map = {}
    for cr in existing_instance_list:
        existing_instance_map[cr.id] = cr

    def verify_fields():  # useful inner function
        """verify fields.

        :return: :raise ValidationError:
        """

        def recursive_verify(field_list, existing, in_data, parent_field_str):
            """recursive verify.

            :param field_list:
            :param existing:
            :param in_data:
            :param parent_field_str:
            :raise ValidationError:
            """
            for field in field_list:
                if isinstance(field, dict):
                    for k in field.keys():
                        model_instance = get_model_field_value(existing, k)
                        if not model_instance:
                            raise ValidationError(
                                {parent_field_str: '{} field not found in ' +
                                    'model {}'.format(k, type(existing))})
                        in_data_value = in_data.get(k, None)
                        if not in_data_value:
                            raise ValidationError(
                                {parent_field_str: '{} field required'.
                                    format(k)})
                        recursive_verify(
                            field.get(k),
                            model_instance,
                            in_data_value,
                            '{} {} (id: {})'.format(
                                parent_field_str,
                                k,
                                repr(
                                    model_instance.id)))
                else:
                    in_data_value = in_data.get(field, None)
                    if in_data_value:
                        if get_model_field_value(existing, field) \
                                != in_data_value:
                            # noinspection PyPep8
                            raise ValidationError(
                                {parent_field_str: '{} ' + 'value cannot be \
                                 changed by {} to {}'.format(field,
                                 user_role_str, repr(in_data_value))})

        return recursive_verify

    for init_data in intial_data_list:
        in_id = init_data.pop('id', None)
        if not in_id:
            raise ValidationError({list_name_str: 'id is required'})

        existing_instance = existing_instance_map.pop(in_id, None)
        if not existing_instance:
            raise ValidationError(
                {list_name_str: 'missing object with id {}'.
                    format(repr(in_id))})

        validator = verify_fields()
        validator(fields_unchanged_list, existing_instance, init_data,
                  '{} (id: {} )'.format(list_name_str, repr(in_id)))
