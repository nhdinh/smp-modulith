#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from typing import TYPE_CHECKING

from foundation.entity import Entity
from foundation.events import EventMixin
from product_catalog.domain.rules.display_name_must_not_be_empty_rule import DisplayNameMustNotBeEmptyRule
from product_catalog.domain.rules.reference_must_not_be_empty_rule import ReferenceMustNotBeEmptyRule
from product_catalog.domain.value_objects import ProductId

if TYPE_CHECKING:
    from product_catalog.domain.entities.catalog import Catalog
    from product_catalog.domain.entities.collection import Collection


class Product(EventMixin, Entity):
    def __init__(
            self,
            product_id: ProductId,
            reference: str,
            display_name: str,
            collection=None,
            catalog=None,
    ):
        super().__init__()

        self.check_rule(ReferenceMustNotBeEmptyRule(reference=reference))
        self.check_rule(DisplayNameMustNotBeEmptyRule(dn=display_name))

        self._product_id = product_id
        self._reference = reference
        self.display_name = display_name

        # set collection and catalog data
        if collection:
            self._collection = collection  # type: Collection
            self._collection_reference = collection.reference

        if catalog:
            self._catalog = catalog  # type: Catalog
            self._catalog_reference = catalog.reference

    @property
    def product_id(self):
        return self._product_id

    @property
    def reference(self):
        return self._reference

    @property
    def collection(self):
        return self._collection

    @property
    def catalog(self):
        return self._catalog

    @staticmethod
    def create(
            reference: str,
            display_name: str,
            **kwargs
    ):
        product = Product(
            product_id=ProductId(uuid.uuid4()),
            reference=reference,
            display_name=display_name
        )

        return product
