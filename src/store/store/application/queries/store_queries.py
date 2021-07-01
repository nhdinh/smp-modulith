#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import UUID

import marshmallow as ma

from db_infrastructure import GUID
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.value_objects import StoreCollectionReference, StoreCatalogReference, StoreProductReference, \
    StoreProductId, StoreCatalogId
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
    collection_id: GUID
    reference: str
    title: str
    disabled: bool
    default: bool

    def serialize(self):
        return {
            'collection_id': self.collection_id,
            'collection_reference': self.reference,
            'collection_title': self.title,
            'disabled': self.disabled,
            'default': self.default,
        }


@dataclass
class StoreCatalogResponseDto:
    catalog_id: GUID
    store_id: str
    reference: str
    title: str
    default: bool
    disabled: bool
    collections: List[StoreCollectionResponseDto]

    def serialize(self):
        return {
            'catalog_id': str(self.catalog_id),
            'store_id': str(self.store_id),
            'catalog_reference': self.reference,
            'catalog_title': self.title,
            'default': self.default,
            'disabled': self.disabled,
            'collection': [c.serialize() for c in self.collections]
        }


@dataclass
class StoreProductShortResponseDto:
    product_id: GUID
    reference: str
    title: str

    image: str

    brand: str
    catalog: str
    catalog_id: GUID
    created_at: datetime

    def serialize(self):
        return {
            'product_id': self.product_id,
            'title': self.title,
            'image': self.image if self.image else '',
            'catalog': self.catalog,
            'catalog_id': self.catalog_id,
            'brand': self.brand,
            'created_at': self.created_at
        }


@dataclass
class StoreProductResponseDto:
    product_id: GUID
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


@dataclass
class StoreSettingResponseDto:
    name: str
    value: str
    type: str

    def serialize(self):
        return {
            'name': self.name,
            'value': self.value,
            'type': self.type,
        }


@dataclass
class StoreInfoResponseDto:
    store_id: UUID
    store_name: str
    # settings: List[StoreSettingResponseDto] = field(default_factory=list)
    settings: List[StoreSettingResponseDto] = field(metadata={"marshmallow_field": ma.fields.Raw()},
                                                    default_factory=list)

    def serialize(self):
        return {
            'store_id': str(self.store_id),
            'store_name': self.store_name,
            'settings': [setting.serialize() for setting in self.settings]
        }


@dataclass
class StoreWarehouseResponseDto:
    warehouse_id: UUID
    warehouse_name: str
    default: bool
    disabled: bool

    def serialize(self):
        return {
            'warehouse_id': str(self.warehouse_id),
            'warehouse_name': self.warehouse_name,
            'default': self.default,
            'disabled': self.disabled
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


class FetchStoreProductsByCatalogQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, catalog_id: StoreCatalogId, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[
        StoreProductShortResponseDto]:
        pass


class FetchStoreProductsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreProductShortResponseDto]:
        pass


class FetchStoreSettingsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, store_of: str) -> StoreInfoResponseDto:
        pass


class CountStoreOwnerByEmailQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, email: str) -> int:
        pass


class FetchStoreWarehouseQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, warehouse_owner: StoreOwner) -> List[StoreWarehouseResponseDto]:
        pass
