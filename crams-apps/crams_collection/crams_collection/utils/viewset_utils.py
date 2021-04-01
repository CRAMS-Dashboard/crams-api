# coding=utf-8
"""

"""
from crams_collection.constants import api as collection_constants


class ViewsetUtils:
    @classmethod
    def get_eresearch_body_param(cls, http_request):
        return http_request.query_params.get(
            collection_constants.EResearch_Body_NAME_PARAM, None)
