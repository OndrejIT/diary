# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2016-2018

from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe

from .forms import CollectionForm, ItemForm
from .models import Collection, Item, Token


# FIXME dopsat vypis komu patri
class CollectionAdmin(admin.ModelAdmin):
    form = CollectionForm
    list_display = ("name", "items_count_order", "token", "updated")
    fields = ("name", "token", "tags", "updated")
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
            obj.pk,
            obj.items__count
        )

        return href

    items_count_order.short_description = "Záznamy"
    items_count_order.admin_order_field = "items__count"


class ItemAdmin(admin.ModelAdmin):
    form = ItemForm
    list_display = ("name", "collection", "etag", "history_etag", "updated")
    fields = ("name", "vobject", "collection", "etag", "history_etag", "updated")
    readonly_fields = ("updated",)
    actions = ["delete_selected"]


class TokenAdmin(admin.ModelAdmin):
    list_display = ("name", "item", "collection", "etag", "created")
    fields = ("name", "item", "etag", "collection", "created")
    readonly_fields = ("created",)
    actions = ["delete_selected"]


admin.site.register(Collection, CollectionAdmin)
admin.site.register(Token, TokenAdmin)
admin.site.register(Item, ItemAdmin)
