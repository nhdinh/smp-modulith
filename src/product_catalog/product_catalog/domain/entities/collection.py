#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional, Set
from uuid import UUID

from product_catalog.domain.entities.product import Product
from product_catalog.domain.value_objects import CollectionReference


@dataclass(unsafe_hash=True)
class Collection:
    reference: Optional[CollectionReference]
    display_name: str

    @property
    def products(self) -> Set[Product]:
        if hasattr(self, '_products'):
            return self._products
        else:
            return set()
