# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2019

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Item, Collection


@receiver(post_save, sender=Item)
def transaction_commit(sender, instance, **kwargs):
    instance._collections_id = [i.id for i in instance.collection.all()]
    transaction.on_commit(
        lambda: on_transaction_commit(instance)
    )


def on_transaction_commit(instance):
    instance.collections_id = [i.id for i in instance.collection.all()]
    changes = [i for i in instance.collections_id if i not in instance._collections_id] + [i for i in instance._collections_id if i not in instance.collections_id]
    for i in changes:
        try:
            collection = Collection.objects.get(id=i)
            collection.token = ""
            collection.save()
        except Collection.DoesNotExist:
            pass
