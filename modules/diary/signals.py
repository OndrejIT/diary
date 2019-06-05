# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2019

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Collection


@receiver(m2m_changed, sender=Collection.items.through)
def collection_token_reset(instance, **kwargs):
    instance.token = ""
    instance.save()
