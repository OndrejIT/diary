# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2016-2018

from django.contrib.auth.models import AbstractUser
from django.db import models

from modules.diary.models import Collection


class User(AbstractUser):
    """Uzivatel"""

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self._username = self.username if self.pk else None

    collections = models.ManyToManyField(Collection, related_name="users", verbose_name="Kolekce", blank=True)
