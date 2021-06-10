#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from dataclasses import dataclass
from typing import Optional, Set

from slugify import slugify

from store.domain.entities.store_product import StoreProduct
from store.domain.entities.value_objects import StoreCollectionReference, StoreCollectionId


@dataclass(unsafe_hash=True)
class StoreCollection:
    collection_id: StoreCollectionId
    reference: StoreCollectionReference
    display_name: str
    default: bool = False

    @property
    def products(self) -> Set[StoreProduct]:
        if hasattr(self, '_products'):
            return self._products
        else:
            return set()

    @property
    def catalog(self):
        if hasattr(self, '_catalog'):
            return self._catalog

        return None

    @classmethod
    def make_collection(
            cls,
            display_name,
            **kwargs
    ):
        # generate collection_id
        collection_id = kwargs.get('collection_id') if 'collection_id' in kwargs.keys() else StoreCollectionId(
            uuid.uuid4())

        # generate reference
        reference = kwargs.get('reference') if 'reference' in kwargs.keys() else slugify(display_name)
        reference = reference if reference else slugify(display_name)

        # generate is_default
        is_default = kwargs.get('default') if 'default' in kwargs.keys() else False

        return StoreCollection(
            collection_id=collection_id,
            reference=reference,
            display_name=display_name,
            default=is_default
        )

    def __repr__(self):
        return f'<StoreCollection reference="{self.reference}" display_name="{self.display_name}" product_cnt={len(self.products)}>'
