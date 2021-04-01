from rest_framework import viewsets, exceptions, mixins

from crams import models
from crams.utils import rest_utils


class LookupViewset(viewsets.ReadOnlyModelViewSet):
    def get_current_user(self, http_request=None):
        if http_request:
            return http_request.user
        user, _ = rest_utils.get_current_user_from_context(self)
        return user

    def fetch_e_research_body_param_obj(self, erb_name=None):
        if not erb_name:
            erb_name = self.request.query_params.get('e_research_body', None)
        if erb_name:
            try:
                return models.EResearchBody.objects.get(name__iexact=erb_name)
            except models.EResearchBody.DoesNotExist:
                msg = 'EResearchBody with name {} does not exist'
                raise exceptions.ValidationError(msg.format(erb_name))
        return None

    def fetch_system_key_param_obj(self, erb_obj=None, key=None, type=None):
        erb_obj = erb_obj or self.fetch_e_research_body_param_obj()
        if erb_obj:
            key = key or self.request.query_params.get('key', None)
            qs = models.EResearchBodyIDKey.objects.filter(
                        e_research_body=erb_obj, key__iexact=key)
            if type:
                qs = qs.filter(type=type)

            if not qs.exists():
                prefix = 'System ID'
                if type == models.EResearchBodyIDKey.METADATA:
                    prefix = 'Meta label'
                elif type == models.EResearchBodyIDKey.LABEL:
                    prefix = 'Label'
                msg = '{} with key {} does not exist for {}'
                raise exceptions.ValidationError(
                    msg.format(prefix, key, erb_obj))

            return qs.first()
        return None


class CreateListViewset(LookupViewset, mixins.CreateModelMixin):
    pass


class UpdateListViewset(CreateListViewset, mixins.UpdateModelMixin):
    pass
