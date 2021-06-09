#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.domain.entities.value_objects import StoreCatalogReference


@dataclass
class StoreCatalog:
    catalog_reference: StoreCatalogReference
    display_name: str
    display_image: str
    disabled: bool
    system: bool

    def toggle(self):
        self.disabled = not self.disabled
