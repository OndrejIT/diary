# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2016-2018

from lib.admin import PermissionVersionAdmin
from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin

from .models import User


class UserAdmin(OriginalUserAdmin, PermissionVersionAdmin):
    filter_horizontal = ("collections",)
    list_display = ("username", "collections_count_order", "email", "first_name", "last_name", "is_staff")
    fieldsets = OriginalUserAdmin.fieldsets + (
        ("Diary", {
            "fields": ("collections",)
        }),
    )

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        qs = qs.annotate(Count("collections"))
        return qs

    @mark_safe
    def collections_count_order(self, obj):
        href = "<a href={0}?users__id__exact={1}>{2}</a>".format(
            reverse("admin:diary_collection_changelist"),
            obj.id,
            obj.collections__count
        )

        return href

    collections_count_order.short_description = "Kolekce"
    collections_count_order.admin_order_field = "collections__count"


admin.site.register(User, UserAdmin)
