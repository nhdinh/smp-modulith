#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Set

from slugify import slugify

from foundation.entity import Entity
from foundation.events import EventMixin
from product_catalog.domain.entities.collection import Collection
from product_catalog.domain.entities.product import Product
from product_catalog.domain.events import CollectionCreatedEvent
from product_catalog.domain.rules.display_name_must_not_be_empty_rule import DisplayNameMustNotBeEmptyRule
from product_catalog.domain.rules.reference_must_not_be_empty_rule import ReferenceMustNotBeEmptyRule
from product_catalog.domain.value_objects import CatalogId, CatalogReference, CollectionReference


class Catalog(EventMixin, Entity):
    def __init__(
            self,
            reference: CatalogReference,
            display_name: str
    ):
        super(Catalog, self).__init__()

        self.check_rule(ReferenceMustNotBeEmptyRule(reference=reference,
                                                    message='Reference code of the catalog must not be empty'))
        self.check_rule(DisplayNameMustNotBeEmptyRule(dn=display_name,
                                                      message='Display name of the catalog must not be empty'))

        self._reference = reference
        self.display_name = display_name

        self._collections: Set[Collection] = set()
        self._default_collection: Optional[Collection] = None

        self._created_at = datetime.now()

    @property
    def reference(self) -> CatalogReference:
        return self._reference

    @property
    def collections(self) -> Set[Collection]:
        return self._collections

    @property
    def default_collection(self) -> Optional[Collection]:
        return self._default_collection

    def create_child_collection(
            self,
            collection_reference: CollectionReference,
            display_name: str,
            set_default: bool = False
    ) -> Collection:
        """
        Create a child collection in this catalog

        :param collection_reference: reference code of a collection
        :param display_name: display name of the creating collection
        :param set_default: set this collection is default or not?
        """
        # TODO: check rule(s) on:
        self.check_rule(
            DisplayNameMustNotBeEmptyRule(dn=display_name,
                                          message='Display name of the collection must not be empty'))
        self.check_rule(ReferenceMustNotBeEmptyRule(reference=collection_reference,
                                                    message='Reference string of the collection must not be empty'))

        collection = Collection(
            reference=collection_reference,
            display_name=display_name
        )

        self._collections.add(collection)

        if set_default:
            self._default_collection = collection

        self._record_event(CollectionCreatedEvent(
            reference=collection_reference,
            catalog_reference=self.reference
        ))

        return collection

    def __str__(self) -> str:
        return f'<Catalog #{self.reference} display_name="{self.display_name}">'

    def __eq__(self, other: Catalog) -> bool:
        return isinstance(other, Catalog) and vars(self) == vars(other)

    @staticmethod
    def create(reference, display_name, **kwargs):
        catalog = Catalog(
            reference=reference,
            display_name=display_name
        )

        return catalog

    def create_default_collection(self):
        self.create_child_collection(
            collection_reference='default_collection',
            display_name='Default Collection',
            set_default=True)

    def get_child_collection_or_create_new(
            self,
            reference: str,
            display_name: Optional[str] = None
    ):
        """
        Query a child collection by its reference. If such collection is not exists, then create it

        :param reference: reference of the collection
        :param display_name: display name of the collection
        :return: the collection
        """
        try:
            return next(c for c in self._collections if c.reference == reference)
        except StopIteration:
            collection = self.create_child_collection(
                collection_reference=reference,
                display_name=display_name)

            return collection

    def create_product(self, reference, display_name, **kwargs):
        product = Product.create(
            reference=reference,
            display_name=display_name,
            **kwargs
        )

        # check if any collection is existed
        if 'collection_display_name' in kwargs.keys():
            c_display_name = kwargs.get('collection_display_name')
            c_reference = slugify(c_display_name)
            collection = self.get_child_collection_or_create_new(
                reference=c_reference,
                display_name=c_display_name
            )
        else:
            collection = self.default_collection

        # set protected data
        product.catalog_reference = self.reference
        product.collection_reference = collection.reference
        product._collection = collection
        product._catalog = self

        # add product to collection
        collection.products.add(product)

        return product
