# coding=utf-8
"""

"""

import pandas as pd
from crams import models
from crams.utils.role import AbstractCramsRoleUtils
from django.http import HttpResponse
from rest_framework import viewsets

from crams_contact.utils import contact_utils
from crams_reports.constants import report_constants


class CramsReportViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # init variables used later
        self.user = None
        self.roles_dict = None
        self.contact = None
        self.user_erb_system_list = None
        self.e_research_system_param_qs = None
        self.pk = None
        self.setup_params_done = False

    def setup_init_params(self):
        if self.setup_params_done:
            return

        self.user = self.request.user
        self.roles_dict = AbstractCramsRoleUtils.fetch_cramstoken_roles_dict(self.user)

        self.contact = contact_utils.fetch_user_contact_if_exists(self.user)
        self.user_erb_system_list = \
            AbstractCramsRoleUtils.get_authorised_e_research_system_list(self.user)

        erbs_name = self.get_eresearch_system_param(self.request)
        self.e_research_system_param_qs = None
        if erbs_name:
            self.e_research_system_param_qs = \
                models.EResearchBodySystem.objects.filter(
                    name__iexact=erbs_name)

        self.pk = None
        lookup_url_kwarg = \
            self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg and lookup_url_kwarg in self.kwargs:
            self.pk = self.kwargs[lookup_url_kwarg]

        self.setup_params_done = True

    @classmethod
    def render_csv_file(cls, data_dict, save_as_filename, header_col=True):
        df = pd.DataFrame(data_dict)
        csv_data = df.to_csv(index=False)
        response = HttpResponse(csv_data, content_type='text/plain; charset=UTF-8')
        response['Content-Disposition'] = ('attachment; filename={0}'.format(save_as_filename))
        return response
    #
    # def get_serializer_context(self):
    #     context = super().get_serializer_context()
    #     if not context:
    #         context = dict()
    #     self.setup_init_params()
    #     context[report_constants.CONTACT_CONTEXT_KEY] = self.contact
    #     context[report_constants.USER_ERB_SYSTEMS_CONTEXT_KEY] = self.user_erb_system_list
    #     return context

    def list_serializer_data(self, http_request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return serializer.data

    @classmethod
    def get_eresearch_body_param(cls, http_request):
        return http_request.query_params.get(
            report_constants.EResearch_Body_NAME_PARAM, None)

    @classmethod
    def get_eresearch_system_param(cls, http_request):
        return http_request.query_params.get(
            report_constants.EResearch_System_NAME_PARAM, None)
