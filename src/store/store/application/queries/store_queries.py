#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import datetime
from typing import List, OrderedDict

from marshmallow import Schema

from store.domain.entities.value_objects import StoreCollectionReference, StoreCatalogReference, StoreProductReference, \
    StoreProductId
from web_app.serialization.dto import PaginationOutputDto, AuthorizedPaginationInputDto


@dataclass
class StoreProductTagResponseDto:
    tag: str

    def serialize(self):
        return {
            'tag': self.tag
        }


@dataclass
class StoreProductUnitResponseDto:
    unit: str
    conversion_factor: float

    def serialize(self):
        return {
            'unit': self.unit,
            'factor': self.conversion_factor,
            'TODO': 'Finish StoreProductUnitResponseDto'
        }


@dataclass
class StoreCollectionResponseDto:
    collection_id: str
    reference: str
    display_name: str
    disabled: bool
    default: bool

    def serialize(self):
        return {
            'collection_id': self.collection_id,
            'collection_reference': self.reference,
            'collection_display_name': self.display_name,
            'disabled': self.disabled,
            'default': self.default,
        }


@dataclass
class StoreCatalogResponseDto:
    catalog_id: str
    store_id: str
    reference: str
    display_name: str
    system: bool
    disabled: bool
    collections: List[StoreCollectionResponseDto]

    def serialize(self):
        return {
            'catalog_id': str(self.catalog_id),
            'store_id': str(self.store_id),
            'catalog_reference': self.reference,
            'catalog_display_name': self.display_name,
            'system': self.system,
            'disabled': self.disabled,
            'collection': [c.serialize() for c in self.collections]
        }


@dataclass
class StoreProductShortResponseDto:
    product_id: str
    reference: str
    display_name: str

    image: str

    brand: str
    catalog: str
    collection: str
    created_at: datetime

    def serialize(self):
        return {
            'product_id': self.product_id,
            'display_name': self.display_name,
            'image': self.image if self.image else '',
            'catalog': self.catalog,
            'collection': self.collection,
            'brand': self.brand,
            'created_at': self.created_at
        }


@dataclass
class StoreProductResponseDto:
    product_id: str
    reference: str
    display_name: str

    brand: str
    catalog: str
    catalog_reference: str
    collection: str
    collection_reference: str
    created_at: datetime
    updated_at: datetime

    units: List[StoreProductUnitResponseDto]
    tags: List[StoreProductTagResponseDto]

    def serialize(self):
        return {
            'product_id': self.product_id,
            'display_name': self.display_name,
            'catalog': self.catalog,
            'catalog_reference': self.catalog_reference,

            'collection': self.collection,
            'collection_reference': self.collection_reference,

            'brand': self.brand,
            'created_at': self.created_at,
            'updated_at': self.updated_at,

            'tags': getattr(self, 'tags', []),
            'units': [u.serialize() for u in getattr(self, 'units', [])],
        }


class FetchStoreCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreCatalogResponseDto]:
        pass


class FetchStoreCollectionsQuery(abc.ABC):
    @abc.abstractmethod
    def query(
            self,
            catalog_reference: str,
            dto: AuthorizedPaginationInputDto
    ) -> PaginationOutputDto[StoreCollectionResponseDto]:
        pass


class FetchStoreProductsFromCollectionQuery(abc.ABC):
    @abc.abstractmethod
    def query(
            self,
            collection_reference: StoreCollectionReference,
            catalog_reference: StoreCatalogReference,
            dto: AuthorizedPaginationInputDto
    ) -> PaginationOutputDto[StoreProductShortResponseDto]:
        pass


class FetchStoreProductQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, owner_email: str,
              catalog_reference: StoreCatalogReference,
              collection_reference: StoreCollectionReference,
              product_reference: StoreProductReference) -> StoreProductResponseDto:
        pass


class FetchStoreProductByIdQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, owner_email: str, product_id: StoreProductId) -> StoreProductResponseDto:
        pass
