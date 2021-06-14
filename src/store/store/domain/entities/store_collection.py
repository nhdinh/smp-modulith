#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Set, TYPE_CHECKING

from foundation import slugify

if TYPE_CHECKING:
    from store.domain.entities.store import Store
from store.domain.entities.store_product import StoreProduct
from store.domain.entities.value_objects import StoreCollectionReference, StoreCollectionId


@dataclass(unsafe_hash=True)
class StoreCollection:
    collection_id: StoreCollectionId
    reference: StoreCollectionReference
    display_name: str
    default: bool = False
    disabled: bool = False

    @property
    def store(self):
        return getattr(self, '_store', None)

    @store.setter
    def store(self, value: Store):
        setattr(self, '_store', value)
        setattr(self, '_store_id', value.store_id)

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
        collection_id = StoreCollectionId(uuid.uuid4())

        # generate reference
        reference = slugify(kwargs.get('reference')) if 'reference' in kwargs.keys() else slugify(display_name)
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
