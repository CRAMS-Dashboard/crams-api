from django.contrib import admin

from crams_review import models


class ReviewDateAdmin(admin.ModelAdmin):
    def project_title(self, obj):
        return obj.request.project.title

    list_display = ('project_title', 'review_date', 'status',)
    list_filter = ('review_date', 'status',)


class ReviewConfigAdmin(admin.ModelAdmin):
    def erb(self, obj):
        return obj.e_research_body.name

    list_display = ('enable', 'erb',)
    list_filter = ('enable',)


class ReviewContactRoleAdmin(admin.ModelAdmin):
    def role(self, obj):
        return obj.name

    list_display = ('role', 'review_config_id',)
    list_filter = ()


admin.site.register(models.ReviewDate, ReviewDateAdmin)
admin.site.register(models.ReviewConfig, ReviewConfigAdmin)
admin.site.register(models.ReviewContactRole, ReviewContactRoleAdmin)
