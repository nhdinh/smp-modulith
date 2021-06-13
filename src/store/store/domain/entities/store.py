#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Set, List, Any, Optional, Union

from slugify import slugify

from foundation.entity import Entity
from foundation.events import EventMixin
from store.application.usecases.const import ExceptionMessages
from store.domain.entities.setting import Setting
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.value_objects import StoreId, StoreCatalogReference, StoreCollectionReference, StoreCatalogId
from store.domain.events.store_catalog_events import StoreCatalogUpdatedEvent, StoreCatalogToggledEvent, \
    StoreCatalogCreatedEvent, StoreCollectionCreatedEvent
from store.domain.events.store_created_event import StoreCreatedEvent
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
        self.owner_email = self._owner.email
        self._managers = set()

        # initial settings
        if settings and type(settings) is List:
            self._settings = set(settings)
        else:
            self._settings: Set[Setting] = Store.default_settings()

        # its catalog
        self._catalogs = set()  # type:Set[StoreCatalog]
        self._make_default_catalog()

        # raise the event
        self._raise_store_created_event()

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
        # create the store from registrationd data
        store = Store(
            store_id=store_id,
            store_name=store_name,
            store_owner=store_owner
        )

        return store

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
            return self.settings[setting_key]
        else:
            return default_value

    def get_catalog_by_reference(self, catalog_reference: StoreCatalogReference) -> Optional[StoreCatalog]:
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

    def get_catalog_by_id(self, catalog_id: StoreCatalogId) -> Optional[StoreCatalog]:
        if not hasattr(self, '_catalogs'):
            return None

        try:
            catalog = next(c for c in self._catalogs if c.catalog_id == catalog_id)
            return catalog
        except StopIteration:
            return None

    def get_default_catalog(self) -> Optional[StoreCatalog]:
        if not hasattr(self, '_catalogs'):
            return None

        try:
            catalog = next(c for c in self._catalogs if c.system)  # type:StoreCatalog
            return catalog
        except StopIteration:
            return None

    def has_catalog_reference(self, catalog_reference: StoreCatalogReference):
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
        catalog = self.get_catalog_by_reference(catalog_reference=catalog_reference)
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
        catalog = self.get_catalog_by_reference(catalog_reference=catalog_reference)  # type:StoreCatalog
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
        """
        Add the `catalog` into self catalogs children

        :param catalog: the catalog to add
        :return: id of the catalog
        """
        if self.has_catalog_reference(catalog_reference=catalog.reference):
            raise Exception(ExceptionMessages.STORE_CATALOG_EXISTED)

        # assign store_id to children catalog and collection
        catalog.store_id = self.store_id
        for collection in catalog.collections:
            collection.store_id = self.store_id

        self._catalogs.add(catalog)

        # add collection event

        # add catalog event
        self._raise_catalog_created_event(catalog=catalog)

        return catalog.catalog_id

    def make_children_catalog(self, reference: str, display_name: str):
        """
        Make a new children catalog

        :param reference: reference of the newly catalog
        :param display_name: catalog's display name
        :return: instance of `StoreCatalog`
        """
        catalog = StoreCatalog.make_catalog(
            display_name=display_name,
            reference=reference,
            store_settings=self.settings
        )

        # add children to self
        self.add_catalog(catalog)

        return catalog

    def make_children_collection(self, of_catalog: StoreCatalogReference,
                                 display_name: str,
                                 reference: str) -> StoreCollection:
        """
        Make a collection into the children catalog
        :param of_catalog:
        :param display_name:
        :param reference:
        """
        try:
            if not self.has_catalog_reference(of_catalog):
                raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

            catalog = self.get_catalog_by_reference(catalog_reference=of_catalog)  # type:StoreCatalog

            collection = catalog.make_collection(
                reference=reference,
                display_name=display_name
            )

            catalog.add_collection(collection)

            self._raise_collection_created_event(collection=collection)

            return collection
        except Exception as exc:
            raise exc

    def toggle_collection(self, collection: Union[StoreCollection, StoreCollectionReference], **kwargs):
        """
        Toggle disable/ enable property of a `StoreCollection`. Input can be an instance of `StoreCollection` or
        `StoreCollectionReference`. For examples:

        collection = StoreCollection(...)
        store.toggle_collection(collection)
        store.toggle_collection(collection.reference, catalog_reference=collection.catalog.reference)

        If the collection is specified by its reference, then the catalog_reference is need too

        :param collection: The collection to be toggled on or off. Can be instance of `StoreCollection` or
        `StoreCollectionReference`

        :param kwargs:
        """

        # check the input collection and make sure it's a child of any catalog
        _catalog = None
        _collection = None
        if type(collection) is StoreCollection:
            if collection.catalog is None and 'catalog_reference' not in kwargs.keys():
                raise Exception(ExceptionMessages.STORE_CATALOG_MUST_BE_SPECIFIED)

            if collection.catalog is None and 'catalog_reference' in kwargs.keys():
                catalog_reference = kwargs.get('catalog_reference')
                if not type(catalog_reference) is StoreCatalogReference:
                    raise Exception(ExceptionMessages.INVALID_STORE_CATALOG_REFERENCE_FORMAT)

                # check if the catalog is children of this store
                _catalog = self.get_catalog_by_reference(catalog_reference=catalog_reference)
                if not _catalog:
                    raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

                # if catalog found, add this collection into this children list
                _catalog.add_collection(collection)

            if collection.catalog not in self.catalogs:
                raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)
            else:
                _catalog = collection.catalog
                _collection = collection
        elif type(collection) is StoreCollectionReference:
            if 'catalog_reference' not in kwargs.keys():
                raise Exception(ExceptionMessages.STORE_CATALOG_MUST_BE_SPECIFIED)

            catalog_reference = kwargs.get('catalog_reference')
            if not type(catalog_reference) is StoreCatalogReference:
                raise Exception(ExceptionMessages.INVALID_STORE_CATALOG_REFERENCE_FORMAT)

            # valid catalog_reference, search for the catalog and collection
            _catalog = self.get_catalog_by_reference(catalog_reference=catalog_reference)
            if not _catalog:
                raise Exception(ExceptionMessages.STORE_CATALOG_NOT_FOUND)

            _collection = _catalog.get_collection(reference=collection)
            if not _collection:
                raise Exception(ExceptionMessages.STORE_COLLECTION_NOT_FOUND)

        # all fine
        _collection.disabled = not _collection.disabled

    def _make_default_catalog(self) -> StoreCatalog:
        default_catalog_reference = self.get_setting('default_catalog_reference', 'default-catalog')
        default_catalog_name = self.get_setting('default_catalog_name', 'Default Catalog')

        # create the new StoreCatalog as default catalog
        default_catalog = StoreCatalog.make_catalog(
            reference=default_catalog_reference,
            display_name=default_catalog_name,
            display_image='',
            disabled=False,
            system=True,
            include_default_collection=True
        )

        # add children to self
        self.add_catalog(default_catalog)

        return default_catalog

    def _raise_store_created_event(self) -> None:
        """
        Raise all the events related to the newly created store
        """
        self._record_event(StoreCreatedEvent(
            store_id=self.store_id,
            store_name=self.name,
            owner_name=self._owner.email,
            owner_email=self._owner.email,
        ))

        for catalog in self._catalogs:
            self._raise_catalog_created_event(catalog)

    def _raise_catalog_created_event(self, catalog: StoreCatalog):
        """
        Raise all the events related to the newly created catalot
        :param catalog: the catalog instance
        """
        self._record_event(StoreCatalogCreatedEvent(
            store_id=self.store_id,
            catalog_id=catalog.catalog_id,
            catalog_reference=catalog.reference
        ))

        for collection in catalog.collections:
            self._raise_collection_created_event(collection)

    def _raise_collection_created_event(self, collection: StoreCollection):
        self._record_event(StoreCollectionCreatedEvent(
            store_id=self.store_id,
            catalog_id=collection.catalog.catalog_id,
            collection_id=collection.collection_id,
            collection_reference=collection.reference,
        ))

    def move_catalog_content(self, source_reference: StoreCatalogReference,
                             dest_reference: Optional[StoreCatalogReference] = None) -> None:
        """
        Move content of a catalog to another one

        :param source_reference: Reference of a source catalog

        :param dest_reference: Reference of a destination catalog. Specified as 'default' or leave it None to tell
        the method to move to default catalog
        """
        try:
            source_catalog = self.get_catalog_by_reference(catalog_reference=source_reference)

            if not dest_reference or dest_reference == 'default' or dest_reference == '':
                dest_catalog = self.get_default_catalog()
            else:
                dest_catalog = self.get_catalog_by_reference(catalog_reference=dest_reference)

            # make sure that the two catalogs is not identical
            if source_catalog == dest_catalog:
                raise Exception(ExceptionMessages.CANNOT_MOVE_CATALOG_CONTENT_TO_ITSELF)

            # ok, so move now
            while len(source_catalog.collections):
                collection = source_catalog.collections.pop()

                # add collection to catalog, with all to be removed as default
                dest_catalog.add_collection(collection, keep_default=False)

        except Exception as exc:
            raise exc

    def delete_catalog(self, reference: StoreCatalogReference) -> None:
        try:
            ...
        except Exception as exc:
            raise exc
