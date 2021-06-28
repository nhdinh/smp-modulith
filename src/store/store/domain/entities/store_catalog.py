#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass

from foundation.common_helpers import short_id
from store.domain.entities.value_objects import StoreCatalogReference


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
