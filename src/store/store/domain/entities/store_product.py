#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from dataclasses import dataclass

from foundation import slugify
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

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, value):
        self._collection = value

    @classmethod
    def create_product(cls, reference: StoreProductReference, display_name: str):
        product_id = StoreProductId(uuid.uuid4())
        reference = slugify(reference)

        return StoreProduct(
            product_id=product_id,
            reference=reference,
            display_name=display_name
        )
