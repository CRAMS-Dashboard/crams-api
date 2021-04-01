# coding=utf-8
"""
 methods to fetch Lookup Data
"""
from rest_framework.exceptions import ParseError

from crams.models import EResearchBodySystem, EResearchBodyIDKey
from crams.models import FundingScheme, FundingBody
from crams.models import Provider
from crams.models import Question
from crams.models import FORCode


class LookupDataModel:

    """

    :param model:
    """

    def __init__(self, model):
        self.model = model

    def get_lookup_data(self, search_key_dict):
        """

        :param search_key_dict:
        :return: :raise ParseError:
        """
        try:
            return self.model.objects.get(**search_key_dict)
        except self.model.DoesNotExist:
            raise ParseError(self.model.__name__ +
                             ' does not exist for search_key_dict ' +
                             repr(search_key_dict))
        except self.model.MultipleObjectsReturned:
            raise ParseError(self.model.__name__ +
                             ' Multiple objects found for search_key_dict ' +
                             repr(search_key_dict))

    def serialize(self, search_key_dict, serializer):
        """

        :param search_key_dict:
        :param serializer:
        :return: :raise ParseError:
        """
        try:
            return serializer(self.get_lookup_data(search_key_dict)).data
        except Exception:
            raise ParseError(
                self.model.__name__ + ': error serializing data for search' +
                                      '_key_dict ' + repr(search_key_dict))


def get_e_research_system_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(EResearchBodySystem).get_lookup_data(search_key_dict)


def get_question_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(Question).get_lookup_data(search_key_dict)


def get_provider_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(Provider).get_lookup_data(search_key_dict)


def get_system_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(EResearchBodyIDKey).get_lookup_data(search_key_dict)


def get_for_code_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(FORCode).get_lookup_data(search_key_dict)


def get_funding_scheme_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(FundingScheme).get_lookup_data(search_key_dict)


def get_funding_body_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(FundingBody).get_lookup_data(search_key_dict)
