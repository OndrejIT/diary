# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2018-2019


import binascii
import contextlib
import json
import logging
import os
from contextlib import contextmanager
from hashlib import md5
from itertools import chain

import vobject
from django.contrib.auth import get_user_model
from django.db import transaction
from radicale import xmlutils
from radicale.storage import Item, BaseCollection
from radicale.storage import (
    sanitize_path, get_etag, check_and_sanitize_props, )

from modules.diary.models import Collection as DBCollection
from modules.diary.models import Item as DBItem
from modules.diary.models import Token

logger = logging.getLogger("diary")


User = get_user_model()


class Collection(BaseCollection):
    def __init__(self, path, principal=None, folder=None, filesystem_path=None):
        self.path = sanitize_path(path).strip("/")
        self._meta_cache = {}
        self._last_modified = None
        self.attributes = self.path.split("/") if self.path else []
        self.deep_path = len(self.attributes)

    @classmethod
    def static_init(cls):
        pass

    @classmethod
    @contextmanager
    def acquire_lock(cls, mode, user=None):
        logger.debug("acquire_lock")
        yield transaction.atomic()

    @property
    def etag(self):
        # FIXME zlepsit
        """Encoded as quoted-string (see RFC 2616)."""
        logger.debug("etag")
        try:
            collection = DBCollection.objects.get(name=self.attributes[1])
            if collection.token:
                return '"{}"'.format(collection.token)
        except DBCollection.DoesNotExist:
            collection = None

        etag = md5()
        for item in self.get_all():
            etag.update((item.name + "/" + item.etag).encode("utf-8"))
        etag.update(json.dumps(self.get_meta(), sort_keys=True).encode())
        token = etag.hexdigest()

        if collection:
            collection.token = token
            collection.save()

        return token

    @property
    def last_modified(self):
        logger.debug("last_modified")
        # FIXME dodelat vraceni z kolekce pokud neni nastaveno
        return self._last_modified

    @classmethod
    def discover(cls, path, depth="0", child_context_manager=(
                 lambda path, href=None: contextlib.ExitStack())):
        logger.debug("discover")
        sane_path = sanitize_path(path).strip("/")
        attributes = sane_path.split("/") if sane_path else []
        deep_path = len(attributes)

        if deep_path:
            try:
                user = User.objects.get(username=attributes[0])
            except User.DoesNotExist:
                return

        # Zkontrolujeme jestli je kolekce/item a jestli existuje
        if deep_path == 2:
            if user.collections.filter(name=attributes[-1]).exists():
                href = None
            else:
                return
        elif deep_path == 3:
            try:
                collection = user.collections.get(name=attributes[1])
            except DBCollection.DoesNotExist:
                return
            if collection.items.filter(name=attributes[-1]).exists():
                href = attributes.pop()
            else:
                return
        else:
            href = None

        collection = cls(sane_path)

        if href:
            yield collection.get(href)
            return

        yield collection

        if depth == "0":
            return

        for href in collection.list():
            with child_context_manager(sane_path, href):
                yield collection.get(href)

        for i in user.collections.all():
            path = "{0}/{1}".format(user.username, i.name)
            with child_context_manager(path):
                yield cls(path)

    @classmethod
    def create_collection(cls, href, collection=None, props=None):
        logger.debug("create_collection")
        sane_path = sanitize_path(href).strip("/")
        if props:
            username, name = sane_path.split("/")
            tags = dict(props)
            name = tags.get("D:displayname", name)
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return

            collection = DBCollection.objects.create(
                name=name,
                tags=tags,
            )

            collection.users.add(user)

        return cls(sane_path)

    def get(self, href, verify_href=True):
        logger.debug("get")
        item, metadata = self._get_with_metadata(href, verify_href=verify_href)

        return item

    def get_meta(self, key=None):
        logger.debug("get_meta")
        if not key:
            return self._meta_cache

        if self.deep_path >= 2:
            if not self._meta_cache:
                try:
                    collection = DBCollection.objects.get(name=self.attributes[1])

                    self._meta_cache = collection.tags
                    self._last_modified = collection.updated
                except DBCollection.DoesNotExist:
                    self._last_modified = None
                try:
                    check_and_sanitize_props(self._meta_cache)
                except ValueError as e:
                    raise RuntimeError("Failed to load properties of collection ""%r: %s" % (self.path, e)) from e
        else:
            self._meta_cache = {}

        return self._meta_cache.get(key)

    def _get_with_metadata(self, href, verify_href=True):
        logger.debug("_get_with_metadata")

        try:
            collection = DBCollection.objects.get(name=self.attributes[1])
        except DBCollection.DoesNotExist:
            return None, None

        try:
            item = collection.items.get(name=href)
        except DBItem.DoesNotExist:
            return None, None

        vobject_item = vobject.readOne(item.vobject)
        object_item = Item(self, href=href, last_modified=item.updated, item=vobject_item)
        tag, start, end = xmlutils.find_tag_and_time_range(vobject_item)

        return object_item, (tag, start, end)

    def get_all(self):
        logger.debug("get_all")
        return (self.get(href) for href in self.list())

    def get_multi2(self, hrefs):
        logger.debug("get_multi2")
        for href in hrefs:
            yield href, self.get(href)

    def list(self):
        logger.debug("list")
        if self.deep_path <= 1:
            return

        try:
            collection = DBCollection.objects.get(name=self.attributes[1])
        except DBCollection.DoesNotExist:
            return

        for i in collection.items.iterator():
            yield i.name

    def upload(self, href, vobject_item):
        logger.debug("upload")
        object_item = Item(self, href=href, item=vobject_item)

        try:
            collection = DBCollection.objects.get(name=self.attributes[1])
        except DBCollection.DoesNotExist:
            return

        try:
            item = DBItem.objects.get(name=href)
        except DBItem.DoesNotExist:
            item = DBItem.objects.create(
                name=href,
                vobject=vobject_item.serialize(),
                etag=object_item.etag.strip("\""),
            )
            collection.items.add(item)

        else:
            # Overime opravneni
            if not collection.items.filter(name=item.name).exists():
                return

            item.vobject = vobject_item.serialize()
            item.etag = object_item.etag.strip("\"")
            item.history_etag = ""

            item.save()

        # FIXME misto resetu token rovnou pocitat?
        for i in item.collections.all():
            i.token = ""
            i.save()

        return object_item

    def delete(self, href=None):
        logger.debug("delete")

        try:
            collection = DBCollection.objects.get(name=self.attributes[1])
        except DBCollection.DoesNotExist:
            return

        if href is not None:
            try:
                item = collection.items.get(name=href)
            except DBItem.DoesNotExist:
                pass
            else:
                # FIXME misto resetu token rovnou pocitat?
                for i in item.collections.all():
                    i.token = ""
                    i.save()

                item.delete()

        else:
            collection.delete()

    def sync(self, old_token=None):
        logger.debug("sync")
        # The sync token has the form http://radicale.org/ns/sync/TOKEN_NAME
        # where TOKEN_NAME is the md5 hash of all history etags of present and
        # past items of the collection.
        def check_token_name(token_name):
            if len(token_name) != 32:
                return False
            for c in token_name:
                if c not in "0123456789abcdef":
                    return False
            return True

        old_token_name = None
        if old_token:
            # Extract the token name from the sync token
            if not old_token.startswith("http://radicale.org/ns/sync/"):
                raise ValueError("Malformed token: %r" % old_token)
            old_token_name = old_token[len("http://radicale.org/ns/sync/"):]
            if not check_token_name(old_token_name):
                raise ValueError("Malformed token: %r" % old_token)
        # Get the current state and sync-token of the collection.

        if not User.objects.filter(username=self.attributes[0]).exists():
            return

        try:
            collection = DBCollection.objects.get(name=self.attributes[1])
        except DBCollection.DoesNotExist:
            return

        # Pokud je token stejnej, neni zadna zmena, nemusi se token znovu pocitat
        if collection.token == old_token_name:
            token = "http://radicale.org/ns/sync/%s" % collection.token
            return token, ()

        state = {}
        token_name_hash = md5()
        # Find the history of all existing and deleted items
        for href, item in chain(((item.href, item) for item in self.get_all())):
            etag = self._update_history_etag(href, item)
            state[href] = etag
            token_name_hash.update((href + "/" + etag).encode("utf-8"))

        token_name = token_name_hash.hexdigest()
        token = "http://radicale.org/ns/sync/%s" % token_name

        if not collection.token == token_name:
            collection.token = token_name
            collection.save()

        if token_name == old_token_name:
            # Nothing changed
            return token, ()

        old_state = {}
        if old_token_name:
            tokens = Token.objects.filter(collection=collection, name=old_token_name)

            if tokens:
                for t in tokens:
                    old_state.update({t.item: t.etag})
            for i in state:
                Token.objects.create(collection=collection, name=token_name, item=i, etag=state[i])

        changes = []
        # Find all new, changed and deleted (that are still in the item cache)
        # items
        for href, etag in state.items():
            if etag != old_state.get(href):
                changes.append(href)
        # Find all deleted items that are no longer in the item cache
        for href, etag in old_state.items():
            if href not in state:
                changes.append(href)
        return token, changes

    def _update_history_etag(self, href, item):
        logger.debug("_update_history_etag")
        try:
            item = DBItem.objects.get(name=href)
        except DBItem.DoesNotExist:
            return

        if not item.history_etag:
            history_etag = binascii.hexlify(os.urandom(16)).decode("ascii")
            item.history_etag = get_etag(history_etag + "/" + item.etag).strip("\"")
            item.save()

        return item.history_etag

    def set_meta_all(self, props):
        logger.debug("set_meta_all")
        delta_props = self.get_meta()
        for key in delta_props.keys():
            if key not in props:
                delta_props[key] = None
        delta_props.update(props)

        if len(self.attributes) >= 2:
            try:
                collection = DBCollection.objects.get(name=self.attributes[1])
                collection.tags.update(delta_props)
                collection.save()
            except DBCollection.DoesNotExist:
                return
