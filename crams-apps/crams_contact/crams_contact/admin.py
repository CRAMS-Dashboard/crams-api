from django.contrib import admin

from crams_contact import models


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


class EResearchContactIdentifierAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'contact',
                    'system', 'parent_erb_contact_id', 'provision_details')
    list_filter = ['provision_details__status', 'system', 'contact']


class OrganisationAdmin(admin.ModelAdmin):
    """
    class OrganisationAdmin
    """
    list_display = ('name', 'short_name', 'ands_url')


class ContactRoleAdmin(admin.ModelAdmin):
    """
    class ContactRoleAdmin
    """
    list_display = ('name', 'project_leader', 'e_research_body', 'read_only')
    list_filter = ['e_research_body', 'project_leader']


class EResearchContactIdentifierAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'contact',
                    'system', 'parent_erb_contact_id', 'provision_details')
    list_filter = ['provision_details__status', 'system', 'contact']


class DelegatesInline(admin.TabularInline):
    model = models.CramsERBUserRoles.delegates.through
    verbose_name = "Delegate"
    verbose_name_plural = "Delegates"


class ErbSystemAdminInline(admin.TabularInline):
    model = models.CramsERBUserRoles.admin_erb_systems.through
    verbose_name = "Admin ERB System"
    verbose_name_plural = "Admin ERB Systems"


class ErbSystemApproverInline(admin.TabularInline):
    model = models.CramsERBUserRoles.approver_erb_systems.through
    verbose_name = "Approver ERB System"
    verbose_name_plural = "Approver ERB Systems"


class ProviderInline(admin.TabularInline):
    model = models.CramsERBUserRoles.providers.through
    verbose_name = "Provider"
    verbose_name_plural = "Providers"


class CramsERBUserRolesAdmin(admin.ModelAdmin):
    list_display = ('contact', 'role_erb', 'is_erb_admin')
    inlines = [
        DelegatesInline,
        ErbSystemAdminInline,
        ErbSystemApproverInline,
        ProviderInline
    ]
    exclude = ('delegates', 'admin_erb_systems',
               'approver_erb_systems', 'providers')


class FacultyAdmin(admin.ModelAdmin):
    """
    class FacultyAdmin
    """
    list_display = ('name', 'organisation', 'faculty_code')
    list_filter = ['organisation']


class SupportEmailContactAdmin(admin.ModelAdmin):
    """
    class SupportEmailContact
    """
    list_display = ('description', 'email',
                    'e_research_body', 'e_research_system')
    list_filter = ['e_research_body', 'e_research_system']


class OrganisationContactAdmin(admin.ModelAdmin):
    """
    class UserRoleAdmin
    """
    list_display = ('contact', 'organisation', 'faculty', 'department')
    list_filter = ['contact', 'faculty', 'organisation']


class ContactFacultyAdmin(admin.ModelAdmin):
    """
    class ContactFacultyAdmin
    """
    list_display = ('contact', 'faculty', 'archived_ts', 'type', 'school_name')
    list_filter = ['faculty', 'contact', 'type', 'contact__email']


admin.site.register(models.ContactDetail, ContactDetailAdmin)
admin.site.register(models.Contact, ContactAdmin)
admin.site.register(models.ContactRole,  ContactRoleAdmin)
admin.site.register(
    models.EResearchContactIdentifier, EResearchContactIdentifierAdmin)
admin.site.register(models.Organisation, OrganisationAdmin)
# admin.site.register(models.OrganisationContact, OrganisationContactAdmin)
admin.site.register(models.CramsERBUserRoles, CramsERBUserRolesAdmin)
admin.site.register(models.Faculty, FacultyAdmin)
# admin.site.register(models.SupportEmailContact, SupportEmailContactAdmin)
# admin.site.register(models.ContactFaculty, ContactFacultyAdmin)
