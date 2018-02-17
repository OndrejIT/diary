# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2016-2018

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin

from .models import User


class UserAdmin(OriginalUserAdmin):
    filter_horizontal = ("collections",)
    fieldsets = OriginalUserAdmin.fieldsets + (
        ("Diary", {
            "fields": ("collections",)
        }),
    )


admin.site.register(User, UserAdmin)
