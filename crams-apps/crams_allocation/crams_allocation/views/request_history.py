# coding=utf-8
"""

"""

from rest_condition import And, Or
from rest_framework import viewsets
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from django.db.models import Q

from crams_allocation.models import Request
from crams.utils.role import AbstractCramsRoleUtils
from crams.constants import db
from crams_allocation.permissions import IsRequestApprover
from crams_collection.permissions import IsProjectContact
from crams.permissions import IsCramsAuthenticated
from crams_allocation.serializers.request_history import RequestHistorySerializer


class RequestHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
        List of archived project information for given request id <BR>
        usage request_history/?request_id=<int>  <BR>
    """
    serializer_class = RequestHistorySerializer
    permission_classes = [
        And(IsCramsAuthenticated,
            Or(IsProjectContact, IsRequestApprover))]

    def get_queryset(self):
        """
        found all request id or current_request id = request_id and status is not draft (N, D)
        """
        request_id = self.request.query_params.get('request_id', None)
        if not request_id:
            raise ParseError('Request Id parameter is required')

        q_conditions = Q(pk=request_id)
        q_conditions.add(Q(current_request__id=request_id), Q.OR)
        q_conditions.add(~Q(request_status__code__in=db.DRAFT_STATES), Q.AND)

        history_qs = Request.objects.filter(q_conditions).order_by('creation_ts')

        ret_list = list(history_qs)

        return ret_list

    def list(self, http_request, *args, **kwargs):
        qs = self.get_queryset()
        context = dict()
        context['crams_token_dict'] = \
            AbstractCramsRoleUtils.fetch_cramstoken_roles_dict(http_request.user)
        sz = self.serializer_class(qs, context=context, many=True)
        return Response(sz.data)
