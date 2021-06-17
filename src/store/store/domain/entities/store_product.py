#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from dataclasses import dataclass

from typing import Set, Optional

from foundation import slugify
from store.domain.entities.store_unit import StoreProductUnit
from store.domain.entities.value_objects import StoreProductReference, StoreProductId


@dataclass(unsafe_hash=True)
class StoreProduct:
    def __init__(
            self,
            product_id: StoreProductId,
            reference: StoreProductReference,
            display_name: str
    ):
        self.product_id = product_id
        self.reference = reference,
        self.display_name = display_name

        self._collection = None
        self._units = set()  # type:Set[StoreProductUnit]

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, value):
        self._collection = value

    @property
    def units(self) -> Set[StoreProductUnit]:
        return self._units

    @property
    def default_unit(self) -> Optional[StoreProductUnit]:
        if len(self._units) == 0:
            return None

        try:
            return next(sp_unit for sp_unit in self._units if sp_unit.default)
        except StopIteration:
            return None

    @default_unit.setter
    def default_unit(self, value):
        if type(value) is StoreProductUnit:
            self._units.add(value)

    @classmethod
    def create_product(cls, reference: StoreProductReference, display_name: str):
        product_id = StoreProductId(uuid.uuid4())
        reference = slugify(reference)

        return StoreProduct(
            product_id=product_id,
            reference=reference,
            display_name=display_name
        )
