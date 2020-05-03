from django.contrib import admin

from .models import Project, ImageAsset, AudioAsset, VideoAsset, DocumentAsset
# Register your models here.


class ProjectAdmin(admin.ModelAdmin):
    pass


class MediaItemAdmin(admin.ModelAdmin):
    readonly_fields = ['size', 'status_update_timestamp']


admin.site.register(Project, ProjectAdmin)
admin.site.register(ImageAsset, MediaItemAdmin)
admin.site.register(AudioAsset, MediaItemAdmin)
admin.site.register(VideoAsset, MediaItemAdmin)
admin.site.register(DocumentAsset, MediaItemAdmin)

