# coding=utf-8
"""

"""
import logging

from rest_framework.exceptions import ValidationError

from crams.models import ProductCommon, ProvisionDetails
from crams.constants.api import OVERRIDE_READONLY_DATA, DO_NOT_OVERRIDE_PROVISION_DETAILS
from crams.serializers import model_serializers
from crams.utils import lang_utils
from crams_collection.config.collection_config import SYSTEM_APPLICANT_DEFAULT_ROLE
from crams_collection.models import Project
from crams_collection.models import ProjectContact
from crams_collection.serializers import project_contact_serializer
from crams_contact.models import ContactRole
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from crams.serializers.provision_details_serializer import AbstractProvisionDetailsSerializer
from crams_allocation.utils import request_utils

User = get_user_model()
LOG = logging.getLogger(__name__)


class AllocationProvisionDetailsSerializer(AbstractProvisionDetailsSerializer):
    def validate(self, data):
        """validate.

        :param data:
        :return validated_data:
        """
        self.override_data = dict()
        if self.context:
            self.override_data = self.context.get(OVERRIDE_READONLY_DATA, None)

        if data['status'] in ProvisionDetails.SET_OF_SENT:
            msg = 'Allocation Request cannot be updated while being provisioned'
            raise ValidationError({'requests': msg})

        return data

    def _get_new_provision_status(self, existing_status):

        if existing_status == ProvisionDetails.PROVISIONED:
            key = DO_NOT_OVERRIDE_PROVISION_DETAILS
            if self.override_data and self.override_data.get(key, False):
                pass
            else:
                return ProvisionDetails.POST_PROVISION_UPDATE

        return existing_status


class ProductRequestSerializer(model_serializers.CreateOnlyModelSerializer):
    """
    ==> from d3_prod crams.api.v1.serializers.requestSerializer
    """
    PR_CONTEXT = 'pr_context'
    provision_details = serializers.SerializerMethodField(
        method_name='sanitize_provision_details')

    @classmethod
    def show_error_msg_context(cls):
        return {
            cls.PR_CONTEXT: AllocationProvisionDetailsSerializer.show_error_msg_context()
        }

    @classmethod
    def hide_error_msg_context(cls):
        return {
            cls.PR_CONTEXT: AllocationProvisionDetailsSerializer.hide_error_msg_context()
        }

    @classmethod
    def build_context_obj(cls, user_obj, erb_system_obj):
        return {
            cls.PR_CONTEXT: AllocationProvisionDetailsSerializer.build_context_obj(
                user_obj, erb_system_obj)
        }

    def sanitize_provision_details(self, product_request_obj):
        default_pd = AllocationProvisionDetailsSerializer.hide_error_msg_context()
        if self.context:
            pd_context = self.context.get(self.PR_CONTEXT, default_pd)
        else:
            pd_context = default_pd

        pd_serializer = AllocationProvisionDetailsSerializer(
            product_request_obj.provision_details,
            context=pd_context)

        return pd_serializer.data

    @classmethod
    def propagate_provision_details(cls, product_request_instance):
        if product_request_instance:
            pd = product_request_instance.provision_details
            if pd:
                pd.id = None
                pd.save()
                return pd

    @classmethod
    def reset_provision_details(cls, product_request):
        """
            override method in sub-classes
        """
        return False

    def set_applicant_default_role(
            self, current_project, current_user, product):
        """
        If applicant does not have a role in the current project, set a
        default role if configured.
        :param current_project:
        :param current_user:
        :param product:
        :return:
        """

        exists_qs = ProjectContact.objects.filter(
            project=current_project, contact__email__iexact=current_user.email)
        if exists_qs.exists():  # Project Contact exists, roles can vary
            return

        msg = 'Default Product Role setup fail, invalid object '
        if not isinstance(product, ProductCommon):
            raise ParseError(msg + str(type(product)))
        if not isinstance(current_project, Project):
            raise ParseError(msg + str(type(current_project)))
        if not isinstance(current_user, User):
            raise ParseError(msg + str(type(current_user)))

        system_name = lang_utils.strip_lower(
            request_utils.get_product_e_system_name(product))
        expected_role = SYSTEM_APPLICANT_DEFAULT_ROLE.get(system_name)
        if not expected_role:
            return

        try:
            role_obj = ContactRole.objects.get(name=expected_role)
        except ContactRole.DoesNotExist:
            msg = 'Contact role does not exists: '
            raise ParseError(msg + expected_role)

        pc_serializer = project_contact_serializer.ProjectContactSerializer(
            context=self.context)
        obj, created = pc_serializer.add_given_user_as_project_contact(
            current_user, current_project, role_obj)
        return obj, created
