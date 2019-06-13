# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2016-2018

from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe

from lib.admin import PermissionVersionAdmin

from .forms import CollectionForm, ItemForm
from .models import Collection, Item, Token


class CollectionAdmin(PermissionVersionAdmin):
    form = CollectionForm
    date_hierarchy = "created"
    list_display = ("name", "users_count_order", "items_count_order", "token", "updated", "created")
    fields = ("name", "token", "tags", "users", "items", "updated", "created")
    list_filter = ("users", "updated", "created", "users")
    filter_horizontal = ("users", "items")
    readonly_fields = ("updated", "created")

    def get_queryset(self, request):
        qs = super(CollectionAdmin, self).get_queryset(request)
        qs = qs.annotate(Count("items", distinct=True), Count("users", distinct=True))

        return qs

    @mark_safe
    def items_count_order(self, obj):
        href = "<a href={0}?collections__id__exact={1}>{2}</a>".format(
            reverse("admin:diary_item_changelist"),
            obj.id,
            obj.items__count
        )

        return href

    items_count_order.short_description = "Záznamy"
    items_count_order.admin_order_field = "items__count"

    @mark_safe
    def users_count_order(self, obj):
        href = "<a href={0}?collections__id__exact={1}>{2}</a>".format(
            reverse("admin:auth_user_changelist"),
            obj.id,
            obj.users__count
        )
        return href

    users_count_order.short_description = "Vlastníci"
    users_count_order.admin_order_field = "users__count"


class ItemAdmin(PermissionVersionAdmin):
    form = ItemForm
    date_hierarchy = "created"
    list_display = ("name", "etag", "history_etag", "updated", "created")
    fields = ("name", "vobject", "etag", "history_etag", "updated", "created")
    list_filter = ("updated", "created", "collections")
    readonly_fields = ("updated", "created")

    @mark_safe
    def href_collection(self, obj):
        hrefs = ""
        for i in obj.collections.all():
            hrefs += "<a href={0}>{1}</a>".format(
                reverse("admin:diary_collection_change", args=(i.id,)),
                "{0}, ".format(i),
            )

        return hrefs

    href_collection.short_description = "Kolekce"
    href_collection.admin_order_field = "collection"


class TokenAdmin(admin.ModelAdmin):
    date_hierarchy = "created"
    list_display = ("name", "item", "href_collection", "etag", "created")
    fields = ("name", "item", "etag", "collection", "created")
    list_filter = ("collection", "created")
    readonly_fields = ("created",)

    @mark_safe
    def href_collection(self, obj):
        href = "<a href={0}>{1}</a>".format(
            reverse("admin:diary_collection_change", args=(obj.collection.id,)),
            obj.collection,
        )

        return href

    href_collection.short_description = "Kolekce"
    href_collection.admin_order_field = "collection"


admin.site.register(Collection, CollectionAdmin)
admin.site.register(Token, TokenAdmin)
admin.site.register(Item, ItemAdmin)
