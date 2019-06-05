# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2019

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Item, Collection


@receiver(post_save, sender=Collection)
def transaction_commit(sender, instance, **kwargs):
    instance._items_id = [i.id for i in instance.items.all()]
    transaction.on_commit(
        lambda: on_transaction_commit(instance)
    )


def on_transaction_commit(instance):
    instance.items_id = [i.id for i in instance.items.all()]
    changes = [i for i in instance.items_id if i not in instance._items_id] + [i for i in instance._items_id if i not in instance.items_id]

    # Pokud se zmeni pocet itemu, resetujeme token.
    # FIXME misto resetu token rovnou pocitat?
    if changes:
        instance.token = ""
        instance.save()
