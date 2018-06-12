# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2017-2018

import itertools

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.text import slugify


class Collection(models.Model):
    """
    Model pro kalendar a kontakty
    """

    @property
    def get_users(self):
        return self.users.all()

    name = models.CharField("Jméno", max_length=254)
    token = models.CharField("Token", max_length=32, blank=True)
    tags = JSONField("Tagy")
    updated = models.DateTimeField("Aktualizováno", auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.name = orig = slugify(self.name)

            for i in itertools.count(1):
                if not Collection.objects.filter(name=self.name).exists():
                    break

                self.name = "{}-{}".format(orig, i)

        super(Collection, self).save(*args, **kwargs)

    class Meta:
        db_table = "collection"
        ordering = ("-id",)
        verbose_name = "Kolekce"
        verbose_name_plural = "Kolekce"


class Item(models.Model):
    """
    Model pro zaznamy
    """

    name = models.CharField("Jméno", max_length=254, unique=True)
    collection = models.ForeignKey(Collection, related_name="items", verbose_name="Kolekce", on_delete=models.CASCADE)
    vobject = models.TextField("Vobject")
    etag = models.CharField("Etag", max_length=32)
    history_etag = models.CharField("History Etag", max_length=32, blank=True)
    updated = models.DateTimeField("Aktualizováno", auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "item"
        ordering = ("-id",)
        verbose_name = "Záznam"
        verbose_name_plural = "Záznamy"


class Token(models.Model):
    """
    Model pro tokeny
    """

    name = models.CharField("Jméno", max_length=254)
    collection = models.ForeignKey(Collection, related_name="tokens", verbose_name="Kolekce", on_delete=models.CASCADE)
    item = models.CharField("Záznam", max_length=254)
    etag = models.CharField("Etag", max_length=32)
    created = models.DateTimeField("Vytvořeno", auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "token"
        ordering = ("-id",)
        verbose_name = "Token"
        verbose_name_plural = "Tokeny"
