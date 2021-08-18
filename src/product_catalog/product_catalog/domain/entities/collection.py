#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional, Set

from foundation.common_helpers import slugify
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
    def make_collection(
            cls,
            display_name,
            **kwargs
    ):
        reference = kwargs.get('reference') if 'reference' in kwargs.keys() else slugify(display_name)
        reference = reference if reference else slugify(display_name)
        is_default = kwargs.get('default') if 'default' in kwargs.keys() else False

        return Collection(
            reference=reference,
            display_name=display_name,
            default=is_default
        )

    def __repr__(self):
        return f'<Collection reference="{self.reference}" display_name="{self.display_name}" product_cnt={len(self.products)}>'
