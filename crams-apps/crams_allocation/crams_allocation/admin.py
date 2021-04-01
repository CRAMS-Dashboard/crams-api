# coding=utf-8
"""
Admin File
"""

from crams import models as crams
from crams_compute import models as compute
from crams_storage import models as storage
from django.contrib import admin
from django.db import models as django_models
from django.forms import Textarea
from django.utils.translation import ugettext_lazy as _

from crams_allocation import models as allocation
from crams_allocation.product_allocation import models as allocation_product


# from rest_framework.authtoken.models import Token


class ParentListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('parent')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'current'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('all', _('all')),
            (None, _('current only')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if not self.value():
            if queryset.model.__name__ == 'Project':
                return queryset.filter(current_project__isnull=True)
            elif queryset.model.__name__ == 'Request':
                return queryset.filter(current_request__isnull=True)
        else:
            return queryset


class RequestAdmin(admin.ModelAdmin):
    """
    class RequestAdmin
    """
    list_display = ('id', 'project', 'funding_scheme', 'start_date',
                    'end_date', 'request_status', 'allocation_extension_count', 'current_request')
    list_filter = [ParentListFilter, 'e_research_system', 'current_request', 'allocation_extension_count']


class EResearchBodyIDKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'e_research_body', 'type')
    list_filter = ['e_research_body', 'type']


class ContactDetailAdmin(admin.ModelAdmin):
    """
    class ContactAdmin
    """
    list_display = ('type', 'email', 'phone', 'parent_contact')


class ContactAdmin(admin.ModelAdmin):
    """
    class ContactAdmin
    """
    list_display = ('given_name', 'surname', 'email')


class FundingSchemeAdmin(admin.ModelAdmin):
    """
    class FundingSchemeAdmin
    """
    list_display = ('id', 'funding_scheme', 'funding_body')


class FundingBodyAdmin(admin.ModelAdmin):
    """
    class FundingBodyAdmin
    """
    list_display = ('id', 'name')


class CramsTokenAdmin(admin.ModelAdmin):
    """
    class FundingBodyAdmin
    """
    list_display = ('user', 'key', 'ks_roles')


class ComputeRequestInline(admin.TabularInline):
    """
    class ComputeRequestInline
    """
    model = allocation_product.ComputeRequest


class StorageRequestInline(admin.TabularInline):
    """
    class StorageRequestInline
    """
    model = allocation_product.StorageRequest


class ProvisionDetailsAdmin(admin.ModelAdmin):
    """
    class ProvisionDetailsAdmin
    """
    list_display = ('id', 'status', 'last_modified_ts', 'creation_ts',
                    'parent_provision_details')
    inlines = [
        ComputeRequestInline,
        StorageRequestInline
    ]


class StorageProductAdmin(admin.ModelAdmin):
    """
    class StorageProductAdmin
    """
    list_display = ('id', 'name', 'zone', 'provider', 'storage_type',
                    'unit_cost', 'operational_cost')
    list_filter = ['e_research_system__e_research_body']


class StorageRequestAdmin(admin.ModelAdmin):
    """
    class StorageRequestAdmin
    """
    list_display = ('id', 'storage_product', 'current_quota',
                    'requested_quota_change', 'approved_quota_change',
                    'provision_id', 'provision_details', 'request')
    list_filter = ['request', 'storage_product', 'provision_id']


class SPProvisionIdAdmin(admin.ModelAdmin):
    """
    class SPProvisionIdAdmin
    """
    list_display = ['id', 'storage_product', 'provision_id']
    list_filter = ['storage_product']


class ComputeRequestAdmin(admin.ModelAdmin):
    """
    class ComputeRequestAdmin
    """
    list_display = (
        'id',
        'instances',
        'cores',
        'core_hours',
        'provision_details',
        'approved_instances',
        'approved_cores',
        'approved_core_hours',
        'request')
    list_filter = ['request', 'compute_product']


class CPProvisionIdAdmin(admin.ModelAdmin):
    """
    class CPProvisionIdAdmin
    """
    list_display = ['id', 'compute_product', 'provision_id']
    list_filter = ['compute_product']


class UserRoleAdmin(admin.ModelAdmin):
    """
    class UserRoleAdmin
    """
    list_display = (
        'id',
        'roles',
        'user'
    )


class EResearchBodySystemAdmin(admin.ModelAdmin):
    """
    class UserRoleAdmin
    """
    list_display = (
        'name',
        'e_research_body',
        'email'
    )


class ERBRequestStatusAdmin(admin.ModelAdmin):
    """
        class ERBRequestStatusAdmin
        """
    list_display = ('display_name', 'request_status',
                    'e_research_system', 'e_research_body', 'extension_count_data_point')
    list_filter = ['request_status', 'extension_count_data_point', 'e_research_body']


class EResearchBodyDelegateAdmin(admin.ModelAdmin):
    """
    class UserRoleAdmin
    """
    list_display = (
        'name',
        'e_research_body',
        'email'
    )


class NotificationTemplateAdmin(admin.ModelAdmin):
    """
    class UserRoleAdmin
    """
    list_display = ('template_file_path', 'request_status',
                    'project_member_status', 'e_research_system')
    list_filter = ['request_status', 'project_member_status',
                   'e_research_system']


class NotificationContactRoleAdmin(admin.ModelAdmin):
    """
    class UserRoleAdmin
    """
    list_display = ('notification', 'contact_role')
    list_filter = ['contact_role', 'notification__e_research_system',
                   'notification__project_member_status']


class MessageOfTheDayAdmin(admin.ModelAdmin):
    """
    class MessageOfTheDayAdmin
    """
    exclude = ('created_by', 'updated_by')
    list_display = ('message', 'creation_ts', 'created_by', 'updated_by')
    list_filter = ['creation_ts', 'created_by', 'updated_by']

    formfield_overrides = {
        django_models.CharField: {'widget': Textarea(attrs={'rows': 6, 'cols': 60})},
    }

    def get_actions(self, request):
        # Disable delete
        actions = super(MessageOfTheDayAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            # new message
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            # editing message
            obj.updated_by = request.user

        obj.save()

    def __init__(self, *args, **kwargs):
        super(MessageOfTheDayAdmin, self).__init__(*args, **kwargs)
        # self.list_display_links = (None,)


class StorageInfrastructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'e_research_body')


class ProjectFacultyAdmin(admin.ModelAdmin):
    """
    class ProjectFacultyAdmin
    """
    list_display = ('project', 'faculty', 'archived_ts')
    list_filter = ['faculty', 'project']


admin.site.register(allocation.Request, RequestAdmin)
# admin.site.register(crams.FundingScheme, FundingSchemeAdmin)
# admin.site.register(crams.FundingBody, FundingBodyAdmin)
# admin.site.register(crams.Provider)
# admin.site.register(crams.CramsToken, CramsTokenAdmin)
admin.site.register(compute.ComputeProduct)
admin.site.register(compute.ComputeProductProvisionId, CPProvisionIdAdmin)
# admin.site.register(crams.EResearchBodyIDKey, EResearchBodyIDKeyAdmin)
# admin.site.register(crams.Question)
admin.site.register(allocation.RequestQuestionResponse)
admin.site.register(allocation_product.StorageRequestQuestionResponse)
admin.site.register(allocation.RequestStatus)
admin.site.register(allocation.ERBRequestStatus, ERBRequestStatusAdmin)
admin.site.register(crams.Zone)
# admin.site.register(crams.ProvisionDetails, ProvisionDetailsAdmin)
admin.site.register(storage.StorageProduct, StorageProductAdmin)
admin.site.register(allocation_product.StorageRequest, StorageRequestAdmin)
admin.site.register(storage.StorageProductProvisionId, SPProvisionIdAdmin)
admin.site.register(allocation_product.ComputeRequest, ComputeRequestAdmin)
# admin.site.register(storage.StorageUsageIngest, StorageUsageIngestAdmin)
# admin.site.register(crams.EResearchBody)
# admin.site.register(crams.EResearchBodySystem, EResearchBodySystemAdmin)
# admin.site.register(crams.EResearchBodyDelegate, EResearchBodyDelegateAdmin)
# admin.site.register(models.IngestSource)
# admin.site.register(notification.NotificationTemplate, NotificationTemplateAdmin)
# admin.site.register(models.NotificationContactRole,
#                     NotificationContactRoleAdmin)

# admin.site.register(crams.MessageOfTheDay, MessageOfTheDayAdmin)
# admin.site.register(storage.StorageInfrastructure, StorageInfrastructureAdmin)
# admin.site.register(collection.ProjectFaculty, ProjectFacultyAdmin)
