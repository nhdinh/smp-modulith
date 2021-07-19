#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class ShopCollection:
    title: str
    default: bool = False
    disabled: bool = False
    deleted: bool = False

    @property
    def catalog(self) -> 'StoreCatalog':
        return getattr(self, '_catalog')

    def __str__(self):
        return f'<StoreCollection #{self.collection_id} catalog="{self.catalog.title}">'

    def __eq__(self, other):
        if not other or not isinstance(other, ShopCollection):
            raise TypeError

        return self.collection_id == other.collection_id or self.title == other.title
