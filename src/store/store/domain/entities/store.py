#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Set, List, Any, Optional, Union

from foundation.entity import Entity
from foundation.events import EventMixin
from store.domain.entities.setting import Setting
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.value_objects import StoreId, StoreCatalogReference
from store.domain.events.store_catalog_events import StoreCatalogUpdatedEvent, StoreCatalogToggledEvent, \
    StoreCatalogCreatedEvent
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
        self._catalogs = {self._make_default_catalog()}  # type:Set[StoreCatalog]

        # build cache
        self._build_cache()

    @property
    def settings(self) -> dict:
        """
        Contains a set of `Setting` that applied to this store

        :return: set of `Setting` data
        """
        return {setting.key: setting.get_value() for setting in self._settings}

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

    @property
    def catalogs(self) -> Set[StoreCatalog]:
        """
        Return a list of children `StoreCatalog`

        :return:
        """
        return self._catalogs

    @classmethod
    def default_settings(cls) -> Set[Setting]:
        settings = set()  # type: Set[Setting]
        settings.add(Setting('default_page_size', '10', 'int'))
        settings.add(Setting('default_catalog_reference', 'unassigned-catalog', 'str'))
        settings.add(Setting('default_catalog_display_name', 'Chưa phân loại', 'str'))
        settings.add(Setting('default_collection_reference', 'unassigned-collection', 'str'))
        settings.add(Setting('default_collection_display_name', 'Chưa phân loại', 'str'))

        return settings

    @classmethod
    def create_store_from_registration(cls, store_id, store_name, store_owner):
        return Store(
            store_id=store_id,
            store_name=store_name,
            store_owner=store_owner
        )

    def update_settings(self, setting_key: str, setting_value: Union[str, int, float]):
        setting = Setting(key=setting_key, value=str(setting_value), type=type(setting_value))
        self._settings.add(setting)

    def has_setting(self, setting_key: str):
        """
        Return the existency of the setting_key in store settlngs selve
        :param setting_key:
        :return:
        """
        return setting_key in self.settings.keys()

    def get_setting(self, setting_key: str, default_value: Any):
        if self.has_setting(setting_key):
            return self.settings['setting_key']
        else:
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
            catalog = next(c for c in self._catalogs if c.reference == catalog_reference)  # type:StoreCatalog
            return catalog
        except StopIteration:
            return None

    def has_catalog(self, catalog_reference: StoreCatalogReference):
        """
        Return the existence of specified `catalog_reference` in this store

        :param catalog_reference: Reference of the catalog to search for
        """

        __cached = getattr(self, '__cached', None)

        if __cached is None or type(__cached) is not dict:
            return False
        elif 'catalogs' not in __cached.keys():
            return False
        else:
            return catalog_reference in __cached['catalogs']

    def update_catalog_data(self, catalog_reference: StoreCatalogReference, update_data: dict) -> None:
        """
        Update the child catalog with input data

        :param catalog_reference: reference of the catalog
        :param update_data:
        """
        catalog = self.get_catalog(catalog_reference=catalog_reference)
        for key, value in update_data.items():
            setattr(catalog, key, value)

        self._record_event(StoreCatalogUpdatedEvent(
            store_id=self.store_id,
            catalog_id=catalog.catalog_id,
            catalog_reference=catalog_reference
        ))

    def toggle_catalog(self, catalog_reference) -> None:
        """
        Toggle the catalog on/ off

        :param catalog_reference: reference of the catalogs
        """
        catalog = self.get_catalog(catalog_reference=catalog_reference)  # type:StoreCatalog
        catalog.toggle()

        self._record_event(StoreCatalogToggledEvent(
            store_id=self.store_id,
            catalog_id=catalog.catalog_id,
            catalog_reference=catalog_reference,
            disabled=catalog.disabled
        ))

    def _build_cache(self):
        # Need to build cache when loading from database. Therefore will need a table that contains all cached data,
        # updated on saved.
        pass

    def add_catalog(self, catalog: StoreCatalog):
        self._catalogs.add(catalog)

        # add catalog event
        self._record_event(StoreCatalogCreatedEvent(
            store_id=self.store_id,
            catalog_id=catalog.catalog_id,
            catalog_reference=catalog.reference,
        ))
        return catalog.catalog_id

    def make_catalog(
            self,
            reference: str,
            display_name: str
    ):
        catalog = StoreCatalog.make_catalog(
            display_name=display_name,
            reference=reference
        )

        # add to self catalogs
        self._catalogs.add(catalog)
        return catalog
