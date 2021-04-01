
from rest_framework import decorators, exceptions
from rest_framework.response import Response

from crams import permissions
from crams.utils import viewset_utils
from crams_log.constants import log_actions
from crams_log.models import CramsLog
from crams_log.serializers import cram_log_sz


class CramsLoginLogViewSet(viewset_utils.LookupViewset):
    """
    # only check if user logged in
    """
    permission_classes = [permissions.IsCramsAuthenticated]
    queryset = CramsLog.objects.none()
    serializer_class = cram_log_sz.CramsLogReadOnlySerializer

    def list(self, request, *args, **kwargs):
        """
        list all login envents order by login time desc
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        referer = request.META.get('HTTP_REFERER')
        # print('-----> referer: {}'.format(referer))
        if not referer:
            referer = 'Referer Unknown'
        user_obj = self.get_current_user()
        if user_obj:
            qs = CramsLog.objects.filter(created_by__iexact=user_obj.email,
                                         action__action_type=log_actions.LOGIN, type__name=referer).order_by(
                '-creation_ts')
            return Response(self.serializer_class(qs, many=True).data)
        # can't find current user email
        err_msg = 'User email not provided'
        raise exceptions.ValidationError(err_msg)

    def get_object(self):
        log_pk = self.kwargs.get('pk')
        try:
            referer = self.request.META.get('HTTP_REFERER')
            # print('-----> referer: {}'.format(referer))
            if not referer:
                referer = 'Referer Unknown'
            qs = CramsLog.objects.get(pk=log_pk, action__action_type=log_actions.LOGIN, type__name=referer)
        except CramsLog.DoesNotExist:
            err_msg = 'CramsLog object with id {} does not exist'.format(log_pk)
            raise exceptions.ValidationError(err_msg)
        return qs

    @decorators.action(detail=False, url_path='last')
    def get_last_login(self, http_request):
        """
        get last login details
        :param http_request:
        :return:
        """
        referer = self.request.META.get('HTTP_REFERER')
        # print('-----> referer: {}'.format(referer))
        if not referer:
            referer = 'Referer Unknown'
        user_obj = self.get_current_user()
        if user_obj:
            qs = CramsLog.objects.filter(created_by__iexact=user_obj.email,
                                         action__action_type=log_actions.LOGIN, type__name=referer).order_by(
                '-creation_ts')
            if qs:
                count = qs.count()
                if count > 1:
                    last_login = qs[1]  # pick the second one as the last login time
                else:
                    # if only the current login, then set creation_ts to None.
                    last_login = qs[0]
                    last_login.creation_ts = None

                return Response(self.serializer_class(last_login).data)
            else:
                return Response(None)
                # can't find current user email
        err_msg = 'User email not provided'
        raise exceptions.ValidationError(err_msg)

# from datetime import datetime
# from django.db.models import Q
# from rest_framework.viewsets import mixins
# from rest_framework.viewsets import GenericViewSet
# from crams_log.serializers.event_log import EventLogSerializer
# class EventLogViewSet(mixins.RetrieveModelMixin, GenericViewSet):
#     # need to enable admin
#     # permission_classes = [permissions.IsCramsAuthenticated]
#     queryset = CramsLog.objects.none()
#     serializer_class = EventLogSerializer
#     start_date = None
#     end_date = None
#
#     # validate project erb against admin erb and can view this project
#     # TODO resolve Project model in code below
#     def is_erb_admin(self, project_id):
#         # try:
#         #     prj = models.Project.objects.get(pk=project_id)
#         #     erbs = prj.requests.all().first().e_research_system
#         #     erb = erbs.e_research_body
#         #
#         #     if roleUtils.is_user_erb_admin(self.request.user, erb_obj=erb):
#         #         return prj
#         #     else:
#         #         raise exceptions.PermissionDenied(
#         #             "User does not hold the correct admin privilege")
#         # except:
#         #     raise exceptions.ParseError('Project id does not exist: ' + project_id)
#         return False
#
#     # get start and end dates
#     def get_dates(self):
#         start_date = self.request.query_params.get('start_date')
#         end_date = self.request.query_params.get('end_date')
#         err_msg = "Date string format incorrect, please use: YYYYmmddHHMMSS or YYYYmmdd"
#
#         # convert to datetime
#         if start_date:
#             try:
#                 sd_dt_obj = datetime.strptime(start_date, '%Y%m%d%H:%M:%S')
#             except:
#                 try:
#                     # NB: default time will be 12:00AM
#                     sd_dt_obj = datetime.strptime(start_date, '%Y%m%d')
#                 except:
#                     raise exceptions.ParseError(err_msg)
#             self.start_date = sd_dt_obj
#
#         if end_date:
#             try:
#                 ed_dt_obj = datetime.strptime(end_date, '%Y%m%d%H:%M:%S')
#             except:
#                 try:
#                     ed_dt_obj = datetime.strptime(end_date, '%Y%m%d')
#                     # set the time of 11:59PM at the end of the day
#                     ed_dt_obj = ed_dt_obj.replace(hour=23, minute=59)
#                 except:
#                     raise exceptions.ParseError(err_msg)
#             self.end_date = ed_dt_obj
#
#     def retrieve(self, request, *args, **kwargs):
#         # get project and validate user has admin access to project
#         project_id = kwargs['pk']
#         prj = self.is_erb_admin(project_id)
#
#         # get the start and end dates
#         self.get_dates()
#
#         # get current project
#         # TODO fix prj below
#         if prj and prj.current_project is not None:
#             prj = prj.current_project
#
#         # fetch all child projects ids
#         prj_list = list()
#         # TODO resolve Project Model below
#         # prj_list = list(models.Project.objects.filter
#         #                 (current_project=prj).values_list('id', flat=True))
#         # prj_list.append(prj.id)  # append the parent prj
#
#         # get the current req
#         req = prj.requests.all().first()
#         if req.current_request is not None:
#             req = req.current_request
#
#         # fetch all child request ids
#         req_list = list()
#         # TODO resolve Request model below
#         # req_list = list(models.Request.objects.filter(
#         #     current_request=req).values_list('id', flat=True))
#         # req_list.append(req.id)  # append the parent req
#
#         # build queryset
#         # exclude project contact action to avoid duplication, already covered in project meta
#         queryset = CramsLog.objects.filter(
#             Q(project_logs__crams_project_db_id__in=prj_list) |
#             Q(allocation_logs__crams_request_db_id__in=req_list))
#
#         # add date parameters to the query
#         if self.start_date:
#             queryset = queryset.filter(creation_ts__gte=self.start_date)
#         if self.end_date:
#             queryset = queryset.filter(creation_ts__lte=self.end_date)
#
#         # sort by creation_ts in desecending order
#         queryset = queryset.order_by('-creation_ts')
#
#         # serialize and convert to csv
#         serialized_data = self.serializer_class(queryset, many=True).data
#
#         return Response(serialized_data)
