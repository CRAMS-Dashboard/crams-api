# coding=utf-8
"""
Dashboard Serializer definitions
"""
from rest_framework import serializers
from crams_contact.serializers.lookup_serializers import DepartmentFlatSerializer


class DashboardProjectListSerializer(serializers.Serializer):
    project = serializers.SerializerMethodField()

    e_research_body = serializers.SerializerMethodField()

    alloc_meta_data = serializers.SerializerMethodField()

    class Meta(object):
        fields = ('project', 'e_research_body', 'alloc_meta_data')

    def get_project(self, project_obj):
        dep_data = DepartmentFlatSerializer(
            project_obj.department).data
        return {
            'id': project_obj.id,
            'crams_id': project_obj.crams_id,
            'title': project_obj.title,
            'department': dep_data
        }

    def get_e_research_body(self, project_obj):
        def build_project_ids(erb_project_ids):
            pid_dict = dict()
            for p_id in erb_project_ids:
                pid_dict[p_id.system.key] = p_id.identifier
            return pid_dict

        limit_erb_name = None
        if 'e_research_body' in self.context:
            limit_erb_name = self.context.get('e_research_body').lower()

        project_erb_dict = dict()
        for r in project_obj.requests.all():
            erb = r.e_research_system.e_research_body
            if limit_erb_name:
                if not erb.name.lower() == limit_erb_name:
                    continue

            if erb not in project_erb_dict:
                project_erb_dict[erb] = set()
            project_erb_dict.get(erb).add(r.e_research_system.name)

        ret_list = list()
        for erb, erbs_set in project_erb_dict.items():
            erb_project_ids = project_obj.project_ids.filter(
                system__e_research_body=erb)
            erb_dict = dict()
            erb_dict['name'] = erb.name
            erb_dict['e_research_systems'] = erbs_set
            erb_dict['project_ids'] = build_project_ids(erb_project_ids)
            ret_list.append(erb_dict)
        return ret_list

    def get_alloc_meta_data(self, project_obj):
        # sr_metadata_count = 0
        # # count the child objects
        # for req in project_obj.requests.all():
        #     if req.current_request:
        #         req = req.current_request
        #     qs = StorageAllocationMetadata.objects.filter(
        #         provision_id__storage_requests__request=req,
        #         current_metadata__isnull=True)
        #
        #     sr_metadata_count += len(qs)
        #
        # alloc_meta_data = dict(storage_child_count=sr_metadata_count)
        #
        # # request id which has child objects
        # alloc_meta_data['child_request_id'] = project_obj.requests.all().first().id
        #
        # return alloc_meta_data
        return None
