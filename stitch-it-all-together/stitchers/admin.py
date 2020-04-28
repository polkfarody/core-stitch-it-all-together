from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# Register your models here.

from .models import Stitcher


class StitcherAdminStackedInline(admin.StackedInline):

    model = Stitcher


class StitcherUserAdmin(UserAdmin):

    inlines = (StitcherAdminStackedInline, )


admin.site.unregister(User)

admin.site.register(User, StitcherUserAdmin)



