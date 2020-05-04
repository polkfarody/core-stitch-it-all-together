from django.contrib import admin

from .models import StatusChangeHistory
# Register your models here.


class StatusChangeHistoryAdmin(admin.ModelAdmin):

    readonly_fields = [
        'content_type', 'object_id', 'status', 'timestamp'
    ]


admin.site.register(StatusChangeHistory, StatusChangeHistoryAdmin)
