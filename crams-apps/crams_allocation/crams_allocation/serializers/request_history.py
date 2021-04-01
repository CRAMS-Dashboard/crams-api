from rest_framework import serializers

from crams.utils.lang_utils import strip_lower
from crams_collection.models import ProjectLog
from crams_allocation.utils.request_utils import BaseRequestUtils
from crams.serializers import model_serializers
from crams_allocation.models import Request, AllocationLog
from crams_log import log_process
from crams_allocation.utils import request_utils


class RequestHistorySerializer(model_serializers.ReadOnlyModelSerializer):
    """class RequestHistorySerializer."""

    project = serializers.SerializerMethodField()

    allocation_request_update_ts = serializers.SerializerMethodField()

    updated_by = serializers.SerializerMethodField()

    request_status = serializers.SerializerMethodField()

    log_messages = serializers.SerializerMethodField()

    class Meta(object):
        model = Request
        fields = ('id', 'request_status', 'project', 'transaction_id',
                  'allocation_request_update_ts', 'last_modified_ts',
                  'current_request', 'updated_by', 'log_messages', 'creation_ts')

    @classmethod
    def get_project(cls, request):
        return {
            'id': request.project.id,
            'title': request.project.title
        }

    def get_allocation_request_update_ts(self, request):
        # if extension submitted or application updated use the update_ts
        if request.request_status.code == 'X' or request.request_status.code == 'U':
            log_list = self.get_log_messages(request)
            try:
                # fetch the last log timestamp
                return log_list[-1].get('date_ts')
            except:
                # if no timestamp found in log, default to creation_ts
                pass

        return request.creation_ts

    def get_updated_by(self, request):
        crams_token_dict = self.context.get('crams_token_dict', dict())
        return BaseRequestUtils.get_restricted_updated_by(
            request, crams_token_dict)

    @classmethod
    def get_request_status(cls, request_obj):
        return request_utils.get_erb_request_status_dict(request_obj)

    def get_log_messages(self, request):
        # determine if user is authorised for created_by info
        #  - require admin permission to view this info for Approved/Provisioned
        show_log_created_by = False
        request_updated_by = self.get_updated_by(request)
        if request.updated_by:
            if strip_lower(request_updated_by.get('email')) == strip_lower(request.updated_by.email.lower()):
                show_log_created_by = True

        # qs1 = AllocationLog.fetch_log_qs_for_request_id(request_db_id=request.id)
        # qs2 = ProjectLog.fetch_log_qs(project_db_id=request.project.id)
        ret_list = list()
        # qs = qs1 | qs2
        qs = AllocationLog.fetch_log_qs_for_request_id(request_db_id=request.id)
        for request_log in qs.all().order_by('creation_ts'):
            log_data = {
                'log': request_log.message,
                'date_ts': request_log.creation_ts,
                'created_by': '*** hidden ***'
            }
            if show_log_created_by:
                log_data['created_by'] = request_log.created_by
            ret_list.append(log_data)
        return ret_list
