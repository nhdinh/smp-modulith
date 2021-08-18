#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Set

from shop.domain.entities.shop_collection import ShopCollection
from shop.domain.entities.value_objects import ShopCollectionId


@dataclass(unsafe_hash=True)
class ShopCatalog:
    title: str
    image: str = ''
    disabled: bool = False
    default: bool = False

    @property
    def shop(self) -> 'Shop':
        return getattr(self, '_shop')

    @property
    def collections(self) -> Set[ShopCollection]:
        return getattr(self, '_collections')

    def __str__(self):
        return f'<ShopCatalog #{self.title}>'

    def __eq__(self, other):
        if not other or not isinstance(other, ShopCatalog):
            raise TypeError

        return self.title == other.title

    def get_collection_by_id(self, collection_id: ShopCollectionId) -> Optional[ShopCollection]:
        collections = getattr(self, '_collections')
        if isinstance(collections, Set) and len(collections):
            try:
                collection = next(c for c in collections if c.collection_id == collection_id)
                return collection
            except StopIteration:
                return None

        return None

    def is_collection_exists(self, collection_title: str):
        try:
            collection = next(col for col in self._collections if col.title == collection_title)
        except StopIteration:
            return False
