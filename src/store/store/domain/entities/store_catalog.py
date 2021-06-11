#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from dataclasses import dataclass

from slugify import slugify
from typing import TYPE_CHECKING, Optional, Set

if TYPE_CHECKING:
    from store.domain.entities.store import Store
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.value_objects import StoreCatalogReference, StoreCatalogId


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
            display_image: str
    ):
        self.catalog_id = catalog_id
        self.reference = reference
        self.display_name = display_name
        self.display_image = display_image
        self.disabled = disabled
        self.system = system

        self._collections = set()
        self._store = None  # type:Store

    @property
    def default_collection(self) -> Optional[StoreCollection]:
        try:
            collection = next(c for c in self._collections if c.default)
            return collection
        except StopIteration:
            return None

    @property
    def collections(self) -> Set[StoreCollection]:
        return self._collections

    def toggle(self):
        self.disabled = not self.disabled

    def get_store_settings(self, setting_key: str, _default_value=None):
        """
        Get setting value from parent store

        :param setting_key: key of the setting
        :param _default_value: default value to return if there is nothing found.
        :return:
        """
        return self._store.get_setting(setting_key=setting_key, default_value=_default_value)

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

        catalog = StoreCatalog(
            catalog_id=catalog_id,
            reference=reference,
            display_name=display_name,
            disabled=False,
            system=is_system,
            display_image=display_image
        )

        if 'included_default_collection' in kwargs.keys():
            collection = kwargs.get('included_default_collection')  # type:StoreCollection
            if type(collection) is StoreCollection:
                collection.default = True
                catalog._collections.add(collection)

        return catalog

    def create_default_collection(self):
        # check if there is any default collection in the list of children
        if self.default_collection:
            return None

        # get settings
        reference = self.get_store_settings('default_collection_reference', 'default_collection')
        display_name = self.get_store_settings('default_collection_display_name', 'Default Collection')
        collection = StoreCollection.make_collection(reference=reference, display_name=display_name, default=True)

        # add the collection into self
        self._collections.add(collection)

        # if the collection is new-ly created, then return (do we need this?)
        return collection
