from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

# Register your models here.

from crams_collection import models as collection


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
            ('all', _('show all')),
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
        else:
            return queryset


class DomainAdmin(admin.ModelAdmin):
    """
     class DomainAdmin
    """
    list_display = ('id', 'percentage', 'project', 'for_code')
    list_filter = (ParentListFilter,)


class PublicationAdmin(admin.ModelAdmin):
    """
     class DomainAdmin
    """
    list_display = ('id', 'reference', 'project')
    list_filter = (ParentListFilter,)


class ProjectQuestionResponseAdmin(admin.ModelAdmin):
    """
     class DomainAdmin
    """
    list_display = ('id', 'question', 'project', 'question_response')
    list_filter = (ParentListFilter,)


class GrantAdmin(admin.ModelAdmin):
    """
     class GrantAdmin
    """
    list_display = ('id', 'grant_type', 'funding_body_and_scheme', 'start_year', 'duration', 'total_funding', 'project')
    list_filter = (ParentListFilter,)


class ProjectAdmin(admin.ModelAdmin):
    """
    class ProjectAdmin
    """
    list_display = ('id', 'title', 'description', 'current_project')
    list_filter = (ParentListFilter,)


class ProjectIDAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'system', 'parent_erb_project_id',
                    'provision_details', 'project')
    list_filter = ['provision_details__status', 'system', 'project']


class ProjectContactAdmin(admin.ModelAdmin):
    """
    class ProjectContactAdmin
    """
    list_display = ('contact', 'contact_role', 'project')
    list_filter = ['contact', 'project', 'contact_role', 'contact__email']


admin.site.register(collection.Project, ProjectAdmin)
admin.site.register(collection.Domain, DomainAdmin)
admin.site.register(collection.Grant, GrantAdmin)
admin.site.register(collection.Publication, PublicationAdmin)
admin.site.register(collection.ProjectContact, ProjectContactAdmin)
admin.site.register(collection.ProjectID, ProjectIDAdmin)
admin.site.register(collection.ProjectQuestionResponse, ProjectQuestionResponseAdmin)
admin.site.register(collection.ProjectLog)
