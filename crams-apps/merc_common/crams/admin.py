# coding=utf-8
"""
Crams Models admin
"""

from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.db import models as django_models
from django.forms import Textarea
from django.utils.translation import ugettext_lazy as _

from crams import models


# class UserAdmin(auth_admin.UserAdmin):
#     """
#     class UserAdmin
#     """
#     list_display = ('first_name', 'last_name', 'username',
#                     'email', 'is_staff', 'is_superuser', 'is_active')
#
#     list_filter = ['is_staff', 'is_superuser', 'is_active']


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


class DomainAdmin(admin.ModelAdmin):
    """
     class DomainAdmin
    """
    list_display = ('id', 'percentage', 'project', 'for_code')
    list_filter = (ParentListFilter,)


class GrantAdmin(admin.ModelAdmin):
    """
     class GrantAdmin
    """
    list_display = ('id', 'grant_type', 'funding_body_and_scheme', 'start_year', 'duration', 'total_funding', 'project')
    list_filter = (ParentListFilter,)


class RequestAdmin(admin.ModelAdmin):
    """
    class RequestAdmin
    """
    list_display = ('id', 'project', 'funding_scheme', 'start_date',
                    'end_date', 'request_status', 'allocation_extension_count', 'current_request')
    list_filter = [ParentListFilter, 'e_research_system', 'current_request', 'allocation_extension_count']


class ProjectAdmin(admin.ModelAdmin):
    """
    class ProjectAdmin
    """
    list_display = ('id', 'title', 'description', 'current_project')
    list_filter = (ParentListFilter, 'requests__e_research_system')


class ProjectIDAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'system', 'parent_erb_project_id',
                    'provision_details', 'project')
    list_filter = ['provision_details__status', 'system', 'project']


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


class ProjectContactAdmin(admin.ModelAdmin):
    """
    class ProjectContactAdmin
    """
    list_display = ('contact', 'contact_role', 'project')
    list_filter = ['contact', 'project', 'contact_role']


class PublicationAdmin(admin.ModelAdmin):
    """
    class ProjectContactAdmin
    """
    list_display = ('project', 'reference')
    list_filter = ['project']


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


class EResearchBodySystemAdmin(admin.ModelAdmin):
    """
    class EResearchBodySystemAdmin
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
    class EResearchBodyDelegateAdmin
    """
    list_display = (
        'name',
        'e_research_body',
        'email'
    )


class EResearchContactIdentifierAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'contact',
                    'system', 'parent_erb_contact_id', 'provision_details')
    list_filter = ['provision_details__status', 'system', 'contact']


class SupportEmailContactAdmin(admin.ModelAdmin):
    """
    class SupportEmailContact
    """
    list_display = ('description', 'email',
                    'e_research_body', 'e_research_system')
    list_filter = ['e_research_body', 'e_research_system']


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
        if actions and 'delete_selected' in actions:
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
        self.list_display_links = ()


admin.site.register(models.User, auth_admin.UserAdmin)
admin.site.register(models.FundingScheme, FundingSchemeAdmin)
admin.site.register(models.FundingBody, FundingBodyAdmin)
admin.site.register(models.Provider)
admin.site.register(models.CramsToken, CramsTokenAdmin)
admin.site.register(models.EResearchBodyIDKey, EResearchBodyIDKeyAdmin)
admin.site.register(models.Question)
admin.site.register(models.EResearchBody)
admin.site.register(models.EResearchBodySystem, EResearchBodySystemAdmin)
admin.site.register(models.EResearchBodyDelegate, EResearchBodyDelegateAdmin)
admin.site.register(models.SupportEmailContact, SupportEmailContactAdmin)
admin.site.register(models.MessageOfTheDay, MessageOfTheDayAdmin)
