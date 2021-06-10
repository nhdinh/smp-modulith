#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from dataclasses import dataclass

from slugify import slugify

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

    def toggle(self):
        self.disabled = not self.disabled

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
        reference = kwargs.get('reference') if 'reference' in kwargs.keys() else slugify(display_name)
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
        pass
