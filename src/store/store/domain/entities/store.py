#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Set, List, Any

from foundation.entity import Entity
from foundation.events import EventMixin
from store.domain.entities.setting import Setting
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.value_objects import StoreId
from store.domain.events.store_created_successfully_event import StoreCreatedSuccessfullyEvent
from store.domain.rules.default_passed_rule import DefaultPassedRule


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

        # check rules
        self.check_rule(DefaultPassedRule())

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

        # raise the event
        self._record_event(StoreCreatedSuccessfullyEvent(
            store_name=self.name,
            owner_name=self._owner.email,
            owner_email=self._owner.email,
        ))

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

    @classmethod
    def create_store_from_registration(cls, store_id, store_name, store_owner):
        return Store(
            store_id=store_id,
            store_name=store_name,
            store_owner=store_owner
        )

    def update_settings(self, setting_name: str, setting_value: Any):
        pass

    def has_setting(self, setting_name: str):
        try:
            s = next(s for s in self._settings if s.name == setting_name)
            return s
        except StopIteration:
            return False
