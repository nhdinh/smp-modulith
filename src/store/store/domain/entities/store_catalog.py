#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass

from foundation import short_id
from store.domain.entities.value_objects import StoreCatalogReference


@dataclass(unsafe_hash=True)
class StoreCatalog:
    reference: StoreCatalogReference
    title: str
    display_image: str = ''
    disabled: bool = False
    default: bool = False

    def __str__(self):
        return f'<StoreCatalog #{short_id(self.catalog_id)}>'
