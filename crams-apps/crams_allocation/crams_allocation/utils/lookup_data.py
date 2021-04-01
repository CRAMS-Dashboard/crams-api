# coding=utf-8
"""
 methods to fetch Lookup Data
"""
from rest_framework.exceptions import ParseError

from crams_storage.models import StorageProduct
from crams_compute.models import ComputeProduct
from crams.models import EResearchBodySystem, EResearchBodyIDKey
# from crams.common.serializers import project_id_serializers
# from crams.common.serializers import lookup_serializers
# from crams.common.serializers import erb_serializers
from crams.utils.model_lookup_utils import LookupDataModel


def get_storage_product_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(StorageProduct).get_lookup_data(search_key_dict)


def get_e_research_system_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(EResearchBodySystem).get_lookup_data(search_key_dict)

# def get_allocation_home_obj(search_key_dict):
#     """
#
#     :param search_key_dict:
#     :return:
#     """
#     return LookupDataModel(models.AllocationHome). \
#         get_lookup_data(search_key_dict)
#
#
# def get_question_obj(search_key_dict):
#     """
#
#     :param search_key_dict:
#     :return:
#     """
#     return LookupDataModel(models.Question). \
#         get_lookup_data(search_key_dict)
#
#
# def get_provider_obj(search_key_dict):
#     """
#
#     :param search_key_dict:
#     :return:
#     """
#     return LookupDataModel(models.Provider).get_lookup_data(search_key_dict)
#
#
# def get_grant_type_obj(search_key_dict):
#     """
#
#     :param search_key_dict:
#     :return:
#     """
#     return LookupDataModel(models.GrantType).get_lookup_data(search_key_dict)


def get_system_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(EResearchBodyIDKey). \
        get_lookup_data(search_key_dict)


# def get_request_status_obj(search_key_dict):
#     """
#
#     :param search_key_dict:
#     :return:
#     """
#     return LookupDataModel(models.RequestStatus). \
#         get_lookup_data(search_key_dict)
#
#
# def get_contact_role_obj(search_key_dict):
#     """
#
#     :param search_key_dict:
#     :return:
#     """
#     return LookupDataModel(models.ContactRole). \
#         get_lookup_data(search_key_dict)
#
#
# def get_for_code_obj(search_key_dict):
#     """
#
#     :param search_key_dict:
#     :return:
#     """
#     return LookupDataModel(models.FORCode). \
#         get_lookup_data(search_key_dict)
#
#
# def get_funding_scheme_obj(search_key_dict):
#     """
#
#     :param search_key_dict:
#     :return:
#     """
#     return LookupDataModel(models.FundingScheme). \
#         get_lookup_data(search_key_dict)


def get_compute_product_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(ComputeProduct).get_lookup_data(search_key_dict)


# def get_project_id_obj(search_key_dict):
#     """
#
#     :param search_key_dict:
#     :return:
#     """
#     return LookupDataModel(models.ProjectID).get_lookup_data(search_key_dict)
#
#
# def get_ingest_source_obj(search_key_dict):
#     """
#
#     :param search_key_dict:
#     :return:
#     """
#     return LookupDataModel(models.IngestSource). \
#         get_lookup_data(search_key_dict)
#

# # LookupData Classes
# def get_allocation_home_lookup_data(search_key_dict, serializer):
#     """
#
#     :param search_key_dict:
#     :param serializer:
#     :return:
#     """
#     if not serializer:
#         serializer = lookup_serializers.AllocationHomeSerializer
#     return LookupDataModel(models.AllocationHome). \
#         serialize(search_key_dict, serializer)
#
#
# def get_provider_lookup_data(search_key_dict, serializer):
#     """
#
#     :param search_key_dict:
#     :param serializer:
#     :return:
#     """
#     if not serializer:
#         serializer = lookup_serializers.ProviderSerializer
#     return LookupDataModel(models.Provider). \
#         serialize(search_key_dict, serializer)
#
#
# def get_grant_type_lookup_data(search_key_dict, serializer):
#     """
#
#     :param search_key_dict:
#     :param serializer:
#     :return:
#     """
#     if not serializer:
#         serializer = lookup_serializers.GrantTypeSerializer
#     return LookupDataModel(models.GrantType). \
#         serialize(search_key_dict, serializer)
#
#
# def get_system_lookup_data(search_key_dict, serializer):
#     """
#
#     :param search_key_dict:
#     :param serializer:
#     :return:
#     """
#     if not serializer:
#         serializer = erb_serializers.EResearchBodyIDKeySerializer
#     return LookupDataModel(models.EResearchBodyIDKey).serialize(
#         search_key_dict, serializer)
#
#
# def get_request_status_lookup_data(search_key_dict, serializer):
#     """
#
#     :param search_key_dict:
#     :param serializer:
#     :return:
#     """
#     if not serializer:
#         serializer = lookup_serializers.RequestStatusSerializer
#     return LookupDataModel(models.RequestStatus). \
#         serialize(search_key_dict, serializer)
#
#
# def get_contact_role_lookup_data(search_key_dict, serializer):
#     """
#
#     :param search_key_dict:
#     :param serializer:
#     :return:
#     """
#     if not serializer:
#         serializer = lookup_serializers.ContactRoleSerializer
#     return LookupDataModel(models.ContactRole). \
#         serialize(search_key_dict, serializer)
#
#
# def get_for_code_lookup_data(search_key_dict, serializer):
#     """
#
#     :param search_key_dict:
#     :param serializer:
#     :return:
#     """
#     if not serializer:
#         serializer = lookup_serializers.FORCodeSerializer
#     return LookupDataModel(models.FORCode). \
#         serialize(search_key_dict, serializer)
#
#
# def get_funding_scheme_lookup_data(search_key_dict, serializer):
#     """
#
#     :param search_key_dict:
#     :param serializer:
#     :return:
#     """
#     if not serializer:
#         serializer = lookup_serializers.FundingSchemeSerializer
#     return LookupDataModel(models.FundingScheme). \
#         serialize(search_key_dict, serializer)
#
#
# def get_compute_product_lookup_data(search_key_dict, serializer):
#     """
#
#     :param search_key_dict:
#     :param serializer:
#     :return:
#     """
#     if not serializer:
#         serializer = lookup_serializers.ComputeProductSerializer
#     return LookupDataModel(models.ComputeProduct). \
#         serialize(search_key_dict, serializer)
#
#
# def get_storage_product_lookup_data(search_key_dict, serializer):
#     """
#
#     :param search_key_dict:
#     :param serializer:
#     :return:
#     """
#     if not serializer:
#         serializer = lookup_serializers.StorageProductSerializer
#     return LookupDataModel(models.StorageProduct). \
#         serialize(search_key_dict, serializer)
#
#
# def get_project_id_lookup_data(search_key_dict, serializer):
#     """
#
#     :param search_key_dict:
#     :param serializer:
#     :return:
#     """
#     if not serializer:
#         serializer = project_id_serializers.ERBProjectIDSerializer
#     return LookupDataModel(models.ProjectID). \
#         serialize(search_key_dict, serializer)
#
#
# def get_e_research_system_lookup_data(search_key_dict, serializer):
#     """
#
#     :param search_key_dict:
#     :param serializer:
#     :return:
#     """
#     if not serializer:
#         serializer = lookup_serializers.EResearchSystemSerializer
#     return LookupDataModel(models.EResearchBodySystem). \
#         serialize(search_key_dict, serializer)
#
#
# def get_e_research_body_lookup_data(search_key_dict, serializer):
#     """
#
#     :param search_key_dict:
#     :param serializer:
#     :return:
#     """
#     if not serializer:
#         serializer = lookup_serializers.EResearchBodySerializer
#     return LookupDataModel(models.EResearchBody). \
#         serialize(search_key_dict, serializer)
