#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Set

from store.domain.entities.store_collection import StoreCollection


@dataclass(unsafe_hash=True)
class StoreCatalog:
    title: str
    image: str = ''
    disabled: bool = False
    default: bool = False

    @property
    def store(self) -> 'Store':
        return getattr(self, '_store')

    @property
    def collections(self) -> Set[StoreCollection]:
        return getattr(self, '_collections')

    def __str__(self):
        return f'<StoreCatalog #{self.catalog_id}>'

    def __eq__(self, other):
        if not other or not isinstance(other, StoreCatalog):
            raise TypeError

        return self.title == other.title or self.catalog_id == other.catalog_id
