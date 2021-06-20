#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from dataclasses import dataclass
from typing import Set, Optional, List

from foundation import slugify
from store.application.usecases.const import ExceptionMessages
from store.domain.entities.store_product_brand import StoreProductBrandReference
from store.domain.entities.store_product_tag import StoreProductTag
from store.domain.entities.store_unit import StoreProductUnit
from store.domain.entities.value_objects import StoreProductReference, StoreProductId


@dataclass(unsafe_hash=True)
class StoreProduct:
    product_id: StoreProductId
    reference: StoreProductReference
    brand_reference: StoreProductBrandReference

    display_name: str
    image: str

    def __init__(
            self,
            product_id: StoreProductId,
            reference: StoreProductReference,
            display_name: str,
            store, catalog, collection,
            **kwargs
    ):
        self.product_id = product_id
        self.reference = reference,
        self.display_name = display_name

        self.image = kwargs.get('image')

        # set parent(s) data
        self._store = store
        self._catalog = catalog
        self._collection = collection

        self._brand = None
        self._units = set()  # type:Set[StoreProductUnit]
        self._tags = set()  # type:Set[StoreProductTag]

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, value):
        self._collection = value

    @property
    def catalog(self):
        return self._catalog

    @catalog.setter
    def catalog(self, value):
        self._catalog = value

    @property
    def store(self):
        return self._store

    @store.setter
    def store(self, value):
        self._store = value

    @property
    def units(self) -> Set[StoreProductUnit]:
        return self._units

    @property
    def tags(self) -> Set[StoreProductTag]:
        return self._tags

    @tags.setter
    def tags(self, value: List[StoreProductTag]):
        self._tags = set(value)

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
    def create_product(cls,
                       reference: StoreProductReference,
                       display_name: str,
                       store, catalog, collection):
        product_id = StoreProductId(uuid.uuid4())
        reference = slugify(reference)

        return StoreProduct(
            product_id=product_id,
            reference=reference,
            display_name=display_name,
            store=store,
            catalog=catalog,
            collection=collection
        )

    @property
    def brand(self):
        return self._brand

    @brand.setter
    def brand(self, value):
        setattr(self, '_brand', value)

    def get_unit(self, unit: str) -> Optional[StoreProductUnit]:
        try:
            return next(product_unit for product_unit in self._units if product_unit.unit == unit)
        except StopIteration:
            return None

    def try_to_make_unit(self, unit: str, base_unit: str, conversion_factor: float):
        try:
            _base_unit = self.get_unit(base_unit)
            if not _base_unit:
                raise Exception(ExceptionMessages.PRODUCT_UNIT_NOT_FOUND)

            product_unit = StoreProductUnit(unit=unit, from_unit=_base_unit, conversion_factor=conversion_factor)
            # product_unit.product = self
            return product_unit
        except Exception as exc:
            raise exc

    def delete_unit(self, unit: str):
        try:
            unit_to_delete = self.get_unit(unit=unit)
            if not unit_to_delete:
                raise Exception(ExceptionMessages.PRODUCT_UNIT_NOT_FOUND)

            # else, check if can be deleted
            can_be_delete = True
            for product_unit in self._units:
                if product_unit.base_unit == unit_to_delete:
                    can_be_delete = False

            if can_be_delete:
                self._units.remove(unit_to_delete)
            else:
                raise Exception(ExceptionMessages.CANNOT_DELETE_DEPENDENCY_PRODUCT_UNIT)
        except Exception as exc:
            raise exc

    def __repr__(self):
        return f'<StoreProduct ref={self.reference}>'
