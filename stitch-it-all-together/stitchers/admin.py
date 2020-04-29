from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from authentication.models import User
from .models import Stitcher


class StitcherAdminStackedInline(admin.StackedInline):

    model = Stitcher


class StitcherUserAdmin(UserAdmin):

    inlines = (StitcherAdminStackedInline, )


admin.site.register(User, StitcherUserAdmin)



