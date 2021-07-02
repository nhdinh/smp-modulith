#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from foundation.common_helpers import short_id

StoreCatalogId = NewType("StoreCatalogId", tp=UUID)
StoreCatalogReference = NewType('StoreCatalogReference', tp=str)


@dataclass(unsafe_hash=True)
class StoreCatalog:
    reference: StoreCatalogReference
    title: str
    display_image: str = ''
    disabled: bool = False
    default: bool = False

    @property
    def store(self) -> 'Store':
        return getattr(self, '_store')

    def __str__(self):
        return f'<StoreCatalog #{short_id(self.catalog_id)}>'

    def __eq__(self, other):
        if not other or not isinstance(other, StoreCatalog):
            raise TypeError

        return self.reference == other.reference and self.title == other.title
