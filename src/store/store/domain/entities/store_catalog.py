#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Set, Dict

from slugify import slugify

from store.application.usecases.const import ExceptionMessages

if TYPE_CHECKING:
    from store.domain.entities.store import Store
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.value_objects import StoreCatalogReference, StoreCatalogId, StoreCollectionReference


class DuplicatedCollectionReferenceError(Exception):
    pass


@dataclass(unsafe_hash=True)
class StoreCatalog:
    reference: StoreCatalogReference
    display_name: str
    display_image: str
    disabled: bool = False
    system: bool = False

    def __init__(
            self,
            catalog_id: StoreCatalogId,
            reference: StoreCatalogReference,
            display_name: str,
            disabled: bool,
            system: bool,
            display_image: str,
            **kwargs
    ):
        self.catalog_id = catalog_id
        self.reference = reference
        self.display_name = display_name
        self.display_image = display_image
        self.disabled = disabled
        self.system = system

        self._collections = set()
        self._store = None  # type: Optional[Store]

        # get settings from store as dict
        self._store_settings = kwargs.get('store_settings') if 'store_settings' in kwargs.keys() else {}  # type: Dict

        # cached
        self.__cached = {
            'collections': set(),
            'products': set()
        }

    @property
    def default_collection(self) -> Optional[StoreCollection]:
        """
        Get the collection which is set as default.

        :return: instance of `StoreCollection`
        """
        if len(self._collections) == 0:
            return None

        try:
            collection = next(c for c in self._collections if c.default)
            return collection
        except StopIteration:
            return None

    @property
    def collections(self) -> Set[StoreCollection]:
        """
        Return a list of children collection

        :return: List of `StoreCollection`
        """
        return self._collections

    def toggle(self):
        """
        Toggle the disabled/enabled feature of this catalog.

        """
        self.disabled = not self.disabled

    def get_store_settings(self, setting_key: str, _default_value=None):
        """
        Get setting value from parent store

        :param setting_key: key of the setting
        :param _default_value: default value to return if there is nothing found.
        :return:
        """
        value = self._store_settings.get(setting_key)
        if not value:
            value = _default_value

        return value

    @classmethod
    def make_catalog(
            cls,
            display_name: str,
            **kwargs) -> StoreCatalog:
        """
        Make and return an instance of StoreCatalog.
        Besides the specified param `display_name`, the method can get additional params like belows:

        * `reference`: Reference name of the catalog

        * `system`: make this catalog as the system catalog, cant be deleted, cant be disabled

        * `display_image`: the image avatar of the catalog

        * `include_default_collection`: create default collection if there is not existence. All the products added
        further to this catalog, will be children of this collection.
        
        :param display_name: Display name of the catalog (mandatory)
        :param kwargs: 
        """
        catalog_id = StoreCatalogId(uuid.uuid4())

        # generate `reference` field
        reference = kwargs.get('reference') if 'reference' in kwargs.keys() else slugify(display_name)
        reference = reference if reference else slugify(display_name)

        # build properties
        is_system = kwargs.get('system') if 'system' in kwargs.keys() else False
        display_image = kwargs.get('display_image') if 'display_image' in kwargs.keys() else ''

        # get store settings
        store_settings = kwargs.get('store_settings') if 'store_settings' in kwargs.keys() else {}

        catalog = StoreCatalog(
            catalog_id=catalog_id,
            reference=reference,
            display_name=display_name,
            disabled=False,
            system=is_system,
            display_image=display_image,
            store_settings=store_settings,
        )

        included_default_collection = kwargs.get(
            'included_default_collection') if 'included_default_collection' in kwargs.keys() else True
        if included_default_collection:
            collection = catalog.create_default_collection()
            catalog.add_collection(collection)

        return catalog

    def create_default_collection(self):
        # check if there is any default collection in the list of children
        if self.default_collection:
            return None

        # get settings
        reference = self.get_store_settings('default_collection_reference', 'default_collection')
        display_name = self.get_store_settings('default_collection_display_name', 'Default Collection')
        collection = StoreCollection.make_collection(reference=reference, display_name=display_name, default=True)

        # if the collection is new-ly created, then return (do we need this?)
        return collection

    def add_collection(self, collection: StoreCollection, rename_if_duplicated=True, keep_default=True):
        """
        Add new collection to this catalog

        :param collection: the collection to be added

        :param rename_if_duplicated: to rename the input collection if its reference has been taken. If set to True,
        the collection's refrence will be added a number into its suffix, else False, the method will raise an
        Exception

        :param keep_default: If keep_default is set True, the collection to be added will be set to Default if its
        default is True. Else, its default property will be set to False.
        """
        if self.has_collection_reference(collection.reference):
            if not rename_if_duplicated:
                raise DuplicatedCollectionReferenceError(ExceptionMessages.DUPLICATED_COLLECTION_REFERENCE_WHEN_COPYING)
            else:
                new_reference = self._make_new_collection_reference(collection.reference)
                collection.reference = new_reference

                # remove default collection if true
                if not keep_default:
                    collection.default = False

        # set store_id for searching further
        collection.store_id = self._store.store_id

        self._collections.add(collection)

    def get_collection(self, reference: StoreCollectionReference) -> Optional[StoreCollection]:
        """
        Get the child collection by it reference

        :param reference: reference to search
        :return: instance of `StoreCollection` or None
        """
        if len(self._collections) == 0:
            return None

        try:
            return next(col for col in self._collections if col.reference == reference)
        except StopIteration:
            return None

    @staticmethod
    def make_collection(reference: StoreCatalogReference, display_name: str):
        """
        Make an instance of a collection

        :param reference: reference of the collection to be created
        :param display_name: display_name of the collection to be created
        :return: instance of a collection
        """
        collection = StoreCollection.make_collection(display_name=display_name, reference=reference)
        return collection

    def has_collection_reference(self, reference: StoreCollectionReference) -> bool:
        """
        Return if the collection reference is list in this catalog's cache

        :param reference: reference of the collection
        :return: True or False
        """
        __cached = getattr(self, '__cached', dict())

        # check if all conditions is good, return the value
        if __cached and 'collections' in __cached.keys() and type(__cached['collections']) is Set:
            return 'reference' in __cached['collections']

        # else, build the value
        if __cached is None or type(__cached) is not Dict:
            setattr(self, '__cached', {'collections': set(), 'products': set()})

        # build cached
        _collection_cache = set()
        for collection in self._collections:
            _collection_cache.add(collection.reference)

        # set cache
        self.__cached['collections'] = _collection_cache

        return reference in self.__cached['collections']

    def _make_new_collection_reference(self, reference: StoreCollectionReference) -> str:
        """
        Search the whole list of collection and make change to the duplicated reference

        :param reference: reference of the collection to change

        :return: a new reference string
        """
        try:
            reference_name_with_number = re.compile(f'^{reference}_([0-9]+)$')
            numbers = []
            for name in self.__cached['collections']:
                matches = reference_name_with_number.match(name)
                if matches:
                    numbers.append(int(matches[1]))

            number_to_change = max(numbers) + 1
            new_reference = f"{reference}_{number_to_change}"

            return new_reference
        except Exception as exc:
            print("Error while finding a new name for collection")
            raise exc
