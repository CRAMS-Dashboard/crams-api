from django.contrib import admin
from crams_manager import models
from crams_contact import models as contact_models


class ServiceManagerAdmin(admin.ModelAdmin):
    list_display = ('contact', 'active')
    model = models.ServiceManager
    model._meta.verbose_name = 'ServiceManager (MeRC Management)'
    model._meta.verbose_name_plural = 'ServiceManagers (MeRC Management)'


class DepartmentManagerAdmin(admin.ModelAdmin):
    list_display = ('contact', 'department', 'active')
    list_filter = ['department', 'department__faculty',
                   'department__faculty__organisation']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "department":
            kwargs["queryset"] = contact_models.Department.objects.all(). \
                order_by('faculty__organisation', 'faculty', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class FacultyManagerAdmin(admin.ModelAdmin):
    list_display = ('contact', 'faculty', 'active')
    list_filter = ['faculty', 'faculty__organisation']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "faculty":
            kwargs["queryset"] = contact_models.Faculty.objects.all(). \
                order_by('organisation', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class OrganisationManagerAdmin(admin.ModelAdmin):
    list_display = ('contact', 'organisation', 'active')


admin.site.register(models.ServiceManager, ServiceManagerAdmin)
admin.site.register(models.DepartmentManager, DepartmentManagerAdmin)
admin.site.register(models.FacultyManager, FacultyManagerAdmin)
admin.site.register(models.OrganisationManager, OrganisationManagerAdmin)
