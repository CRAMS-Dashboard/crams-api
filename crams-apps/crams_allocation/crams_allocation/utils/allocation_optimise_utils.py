# from d3_prod - crams-app.crams.api.v1.dataUtils.optimiseUtils
from django.db.models import Prefetch


class OptimiseProjectRequestUtils:
    @classmethod
    def optimise_request_qs(cls, request_qs, fetch_project_boolean=False):
        qs = request_qs.select_related(
            'current_request', 'request_status', 'funding_scheme',
            'e_research_system__e_research_body'
        ).prefetch_related('storage_requests__storage_product',
                           'storage_requests__provision_details',
                           'compute_requests__compute_product',
                           'compute_requests__provision_details'
                           )

        if not fetch_project_boolean:
            return qs

        qs = qs.select_related('project__current_project')
        return qs

    @classmethod
    def optimise_project_request_qs(cls, project_qs, request_prefetch=None):
        base_qs = project_qs.select_related('current_project')

        if request_prefetch:
            return base_qs.prefetch_related(
                Prefetch('requests', queryset=request_prefetch))

        return base_qs.prefetch_related(
            'requests__e_research_system__e_research_body',
            'requests__current_request',
            'requests__request_status',
            'requests__funding_scheme',
            'requests__storage_requests__storage_product',
            'requests__storage_requests__provision_details',
            'requests__compute_requests__compute_product',
            'requests__compute_requests__provision_details')
