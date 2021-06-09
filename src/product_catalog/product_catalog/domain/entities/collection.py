#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional, Set

from product_catalog.domain.entities.product import Product
from product_catalog.domain.value_objects import CollectionReference


@dataclass(unsafe_hash=True)
class Collection:
    reference: Optional[CollectionReference]
    display_name: str
    default: bool = False

    @property
    def products(self) -> Set[Product]:
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
    def make_collection(cls, reference, display_name):
        return Collection(
            reference=reference,
            display_name=display_name
        )

    def __repr__(self):
        return f'<Collection reference="{self.reference}" display_name="{self.display_name}" product_cnt={len(self.products)}>'
