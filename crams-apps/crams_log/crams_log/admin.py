"""

"""
from django.contrib import admin
from crams_log import models


class CramsLogAdmin(admin.ModelAdmin):
    """
    class LogCommonAdmin
    """
    list_display = ('action', 'type', 'message', 'creation_ts')
    list_filter = ['action', 'type']


class LogActionAdmin(admin.ModelAdmin):
    """
    class LogActionAdmin
    """
    list_display = ('action_type', 'name', 'description')


class LogTypeAdmin(admin.ModelAdmin):
    """
    class LogTypeAdmin
    """
    list_display = ('log_type', 'name', 'description')


class BaseLogAdmin(admin.ModelAdmin):
    @classmethod
    def log_create_ts(cls, instance):
        return instance.log_parent.creation_ts


class AllocationLogAdmin(BaseLogAdmin):
    """
    class AllocationLogAdmin
    """
    list_display = ('crams_request_db_id', 'log_parent', 'log_create_ts')


class ProjectLogAdmin(BaseLogAdmin):
    """
    class ProjectLogAdmin
    """
    list_display = ('crams_project_db_id', 'log_parent', 'log_create_ts')


class ContactLogAdmin(BaseLogAdmin):
    """
    class ContactLogAdmin
    """
    list_display = ('crams_contact_db_id', 'log_parent', 'log_create_ts')


class UserLogAdmin(BaseLogAdmin):
    """
    class ContactLogAdmin
    """
    list_display = ('crams_user_db_id', 'log_parent', 'log_create_ts')


# Register your models here.
admin.site.register(models.LogAction, LogActionAdmin)
admin.site.register(models.LogType, LogTypeAdmin)
admin.site.register(models.CramsLog, CramsLogAdmin)
# admin.site.register(models.ProjectLog, ProjectLogAdmin)
# admin.site.register(models.AllocationLog, AllocationLogAdmin)
# admin.site.register(models.ContactLog, ContactLogAdmin)
admin.site.register(models.UserLog, UserLogAdmin)
