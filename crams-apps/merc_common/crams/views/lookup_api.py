from crams import models
from crams.models import FORCode
from crams.models import FundingScheme
from crams.permissions import IsCramsAuthenticated
from crams.serializers import lookup_serializers
from crams.utils.model_lookup_utils import LookupDataModel
from rest_framework import mixins
from rest_framework import viewsets, decorators
from rest_framework.decorators import api_view
from rest_framework.views import Response


@api_view(http_method_names=['GET'])
def fb_scheme_list(request, fb_name):
    """
    <B>get Funding Scheme for given Funding Body, all if none</B>
    <BR><BR>param fb_name: (optional, case-insensitive) name of the funding body to filter results
    <BR><BR>return: a list of funding schemes, filtered by funding body name if given as parameter to API

    """
    qs = FundingScheme.objects.all()
    if fb_name:
        qs = qs.filter(funding_body__name__iexact=fb_name.lower())

    fs_list = []
    for fs in qs.order_by('id'):
        fs_list.append(lookup_serializers.FundingSchemeSerializer(fs).data)
    return Response(fs_list)


@api_view(http_method_names=['GET'])
def for_codes(request):
    """
    <B>get a list of FOR codes</B>
    <BR><BR>return: a list of FOR code json (Format: {'id':<db_id>, 'desc': '<for code> <description>'})
    """
    for_code_objs = FORCode.objects.all().order_by('code')

    for_codes_list = []
    for for_code in for_code_objs:
        code = for_code.code
        desc = for_code.description
        for_code_dict = {'id': for_code.id, 'desc': '{} {}'.format(code, desc)}
        for_codes_list.append(for_code_dict)
    return Response(for_codes_list)


class EResearchBodySystemViewSet(viewsets.ViewSet):
    serializer_class = None
    # permission_classes = [IsCramsAuthenticated]
    queryset = models.EResearchBody.objects.all()

    @decorators.action(detail=False, url_path='list')
    def fetch_e_research_body(self, request):
        """
        <B>Fetch a list of available eResearch Body</B>
        <BR><BR>:return: a list of eResearch Body
        """
        ret_list = []
        for body in models.EResearchBody.objects.all():
            ret_list.append(body.name)

        return Response(ret_list)

    @decorators.action(detail=False, url_path='e_research_system/(?P<e_research_body>[-\w]+)')
    def fetch_e_research_systems(self, request, e_research_body):
        """
        <B>Given an e_research_body name, this api returns a list of eResearch Systems belonging to it.</B>
        <BR><BR>param: e_research_body: string value of e_research_body name, case insensitive.
        <BR><BR>return: a list of eResearch Systems belonging to the input eResearch body

        """
        ret_list = []
        lookup = LookupDataModel(models.EResearchBody)
        serializer_class = lookup_serializers.EResearchSystemSerializer
        try:
            search_key = {'name__iexact': e_research_body}
            body_obj = lookup.get_lookup_data(search_key)
            qs = body_obj.systems.all()
            ret_list = serializer_class(qs, many=True).data
        except Exception as e:
            pass

        return Response(ret_list)


class SupportEmailContactViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = [IsCramsAuthenticated]
    serializer_class = lookup_serializers.SupportEmailContactSerializer
    queryset = models.SupportEmailContact.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        if 'erb' in self.request.query_params:
            erb = self.request.query_params['erb']
            queryset = self.queryset.filter(e_research_body__name=erb)

        if 'erbs' in self.request.query_params:
            erbs = self.request.query_params['erbs']
            queryset = self.queryset.filter(e_research_system__name=erbs)

        return queryset
