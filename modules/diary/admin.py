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
    list_display = ("name", "items_count_order", "token", "updated")
    fields = ("name", "token", "tags", "updated")
    list_filter = ("users",)
    readonly_fields = ("updated",)
    actions = ["delete_selected"]

    def get_queryset(self, request):
        qs = super(CollectionAdmin, self).get_queryset(request)
        qs = qs.annotate(Count("items"))
        return qs

    @mark_safe
    def items_count_order(self, obj):
        href = "<a href={0}?collection__id__exact={1}>{2}</a>".format(
            reverse("admin:diary_item_changelist"),
            obj.id,
            obj.items__count
        )

        return href

    items_count_order.short_description = "Záznamy"
    items_count_order.admin_order_field = "items__count"


class ItemAdmin(PermissionVersionAdmin):
    form = ItemForm
    list_display = ("name", "href_collection", "etag", "history_etag", "updated")
    fields = ("name", "vobject", "collection", "etag", "history_etag", "updated")
    list_filter = ("collection__users", "collection")
    readonly_fields = ("updated",)
    actions = ["delete_selected"]

    @mark_safe
    def href_collection(self, obj):
        href = "<a href={0}>{1}</a>".format(
            reverse("admin:diary_collection_change", args=(obj.collection.id,)),
            obj.collection,
        )

        return href

    href_collection.short_description = "Kolekce"
    href_collection.admin_order_field = "collection"


class TokenAdmin(admin.ModelAdmin):
    list_display = ("name", "item", "href_collection", "etag", "created")
    fields = ("name", "item", "etag", "collection", "created")
    list_filter = ("collection",)
    readonly_fields = ("created",)
    actions = ["delete_selected"]

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
