#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Set

from foundation import slugify
from store.application.usecases.const import ExceptionMessages

if TYPE_CHECKING:
    from store.domain.entities.store import Store
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.value_objects import StoreCatalogReference, StoreCatalogId, StoreCollectionReference, \
    StoreCollectionId


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

        self._collections = set()  # type:Set[StoreCollection]
        self._store = None  # type: Optional[Store]

        # cached
        self._cached = {
            'collection': set(),
            'products': set()
        }

    @property
    def store(self) -> Store:
        return self._store

    @store.setter
    def store(self, value: Store):
        setattr(self, 'store_id', value.store_id)  # set store_id for the data field
        self._store = value

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
        reference = slugify(kwargs.get('reference')) if 'reference' in kwargs.keys() else slugify(display_name)
        reference = reference if reference else slugify(display_name)

        # build properties
        is_system = kwargs.get('system') if 'system' in kwargs.keys() else False
        display_image = kwargs.get('display_image') if 'display_image' in kwargs.keys() else ''

        catalog = StoreCatalog(
            catalog_id=catalog_id,
            reference=reference,
            display_name=display_name,
            disabled=False,
            system=is_system,
            display_image=display_image
        )

        return catalog

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

        # add the collection to self
        self._collections.add(collection)

    def get_collection_by_reference(self, collection_reference: StoreCollectionReference) -> Optional[StoreCollection]:
        """
        Get the child collection by it reference

        :param collection_reference: reference to search
        :return: instance of `StoreCollection` or None
        """
        if len(self._collections) == 0:
            return None

        try:
            return next(col for col in self._collections if col.reference == collection_reference)
        except StopIteration:
            return None

    def get_collection_by_id(self, collection_id: StoreCollectionId) -> Optional[StoreCollection]:
        if len(self._collections) == 0:
            return None

        try:
            return next(col for col in self._collections if col.collection_id == collection_id)
        except StopIteration:
            return None

    def has_collection_reference(self, reference: StoreCollectionReference) -> bool:
        """
        Return if the collection reference is list in this catalog's cache

        :param reference: reference of the collection
        :return: True or False
        """
        _cached = getattr(self, '_cached', dict())

        # check if all conditions is good, return the value
        if _cached and 'collection' in _cached.keys() and type(_cached['collection']) is Set:
            return 'reference' in _cached['collection']

        # else, build the value
        if _cached is None or type(_cached) is not dict:
            setattr(self, '_cached', {'collection': set(), 'products': set()})

        # build cached
        _collection_cache = set()
        for collection in self._collections:
            _collection_cache.add(collection.reference)

        # set cache
        _cached['collection'] = _collection_cache
        setattr(self, '_cached', _cached)

        return reference in _cached['collection']

    def _make_new_collection_reference(self, reference: StoreCollectionReference) -> str:
        """
        Search the whole list of collection and make change to the duplicated reference

        :param reference: reference of the collection to change

        :return: a new reference string
        """
        try:
            reference_name_with_number = re.compile(f'^{reference}_([0-9]+)$')
            numbers = []
            for name in self._cached['collection']:
                matches = reference_name_with_number.match(name)
                if matches:
                    numbers.append(int(matches[1]))

            number_to_change = max(numbers) + 1 if len(numbers) else 1
            new_reference = f"{reference}_{number_to_change}"

            return new_reference
        except Exception as exc:
            print("Error while finding a new name for collection")
            raise exc
