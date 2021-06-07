#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Set, List

from foundation.entity import Entity
from foundation.events import EventMixin
from store.domain.entities.setting import Setting
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.value_objects import StoreId


class Store(EventMixin, Entity):
    store_id: StoreId

    def __init__(
            self,
            store_id: StoreId,
            store_name: str,
            store_owner: StoreOwner,
            settings: List[Setting] = None
    ):
        super(Store, self).__init__()

        self.store_id = store_id
        self.name = store_name

        # make a list of StoreOwner and Manager
        self._owner = store_owner
        self._managers = set()

        # initial settings
        if settings and type(settings) is List:
            self._settings = set(settings)
        else:
            self._settings: Set[Setting] = Store.default_settings()

    @property
    def settings(self) -> Set[Setting]:
        return self._settings

    @property
    def owner(self) -> StoreOwner:
        return self._owner

    @property
    def managers(self) -> Set:
        return self._managers

    @classmethod
    def default_settings(cls) -> Set[Setting]:
        return set()
