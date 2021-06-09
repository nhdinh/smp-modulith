#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Set, List, Any, Optional

from foundation.entity import Entity
from foundation.events import EventMixin
from store.domain.entities.setting import Setting
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.value_objects import StoreId, StoreCatalogReference
from store.domain.events.store_catalog_events import StoreCatalogUpdatedEvent, StoreCatalogToggledEvent
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

        # its catalog
        self._catalogs = {self._make_default_catalog()}

        # build cache
        self._build_cache()

    @property
    def settings(self) -> Set[Setting]:
        """
        Contains a set of `Setting` that applied to this store

        :return: set of `Setting` data
        """
        return self._settings

    @property
    def owner(self) -> StoreOwner:
        """
        Return an `User` that is owner of this store

        :return: instance of `User`
        """
        return self._owner

    @property
    def managers(self) -> Set:
        """
        Return a list of `User` that are managers of this Store

        :return: set of `User` instances
        """
        return self._managers

    @classmethod
    def default_settings(cls) -> Set[Setting]:
        settings = set()  # type: Set[Setting]
        settings.add(Setting('default_page_size', 10, 'int'))

        return settings

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

    def get_setting(self, setting_key: str, default_value: Any):
        return default_value

    def _make_default_catalog(self) -> StoreCatalog:
        default_catalog_name = self.get_setting('default_catalog_name', 'Default Catalog')
        default_collection_name = self.get_setting('default_collection_name', 'Default Collection')

        return StoreCatalog.make_catalog(
            reference='default_catalog',
            display_name=default_catalog_name,
            display_image='',
            disabled=False,
            system=True,
            include_default_collection=StoreCollection.make_collection(
                reference='default_collection',
                display_name=default_collection_name
            )
        )

    def get_catalog(self, catalog_reference: StoreCatalogReference) -> Optional[StoreCatalog]:
        """
        Get child catalog by catalog_reference

        :param catalog_reference: reference of a catalog to fetch
        :return: instance of `Catalog` or None
        """
        if not hasattr(self, '_catalogs'):
            return None

        try:
            catalog = next(c for c in self._catalogs if c.catalog_reference == catalog_reference)  # type:StoreCatalog
            return catalog
        except StopIteration:
            return None

    def has_catalog(self, catalog_reference: StoreCatalogReference):
        """
        Check if the store contains any catalog with the reference

        :param catalog_reference:
        """
        try:
            return catalog_reference in self.__cached['catalogs']
        except:
            return False

    def update_catalog_data(self, catalog_reference: StoreCatalogReference, update_data: dict) -> None:
        """
        Update the child catalog with input data

        :param catalog_reference: reference of the catalog
        :param update_data:
        """
        catalog = self.get_catalog(catalog_reference=catalog_reference)
        for key, value in update_data.items():
            setattr(catalog, key, value)

        self._record_event(StoreCatalogUpdatedEvent(catalog_reference=catalog_reference))

    def toggle_catalog(self, catalog_reference) -> None:
        """
        Toggle the catalog on/ off

        :param catalog_reference: reference of the catalogs
        """
        catalog = self.get_catalog(catalog_reference=catalog_reference)  # type:StoreCatalog
        catalog.toggle()

        self._record_event(StoreCatalogToggledEvent(catalog_reference=catalog_reference))

    def _build_cache(self):
        # Need to build cache when loading from database. Therefore will need a table that contains all cached data,
        # updated on saved.
        pass
