#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from slugify import slugify

from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.value_objects import StoreCatalogReference


@dataclass
class StoreCatalog:
    catalog_reference: StoreCatalogReference
    display_name: str
    display_image: str
    disabled: bool = False
    system: bool = False

    def __init__(
            self,
            catalog_reference: StoreCatalogReference,
            display_name: str,
            disabled: bool,
            system: bool,
            display_image: str
    ):
        self.catalog_reference = catalog_reference
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
            **kwargs):
        """
        Make and return an instance of StoreCatalog
        
        :param display_name: 
        :param kwargs: 
        """
        reference = kwargs.get('reference') if 'reference' in kwargs.keys() else slugify(display_name)
        is_system = kwargs.get('system') if 'system' in kwargs.keys() else False
        display_image = kwargs.get('display_image') if 'display_image' in kwargs.keys() else ''

        catalog = StoreCatalog(
            catalog_reference=reference,
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
