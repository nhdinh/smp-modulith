#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import List

from store.domain.entities.value_objects import StoreCollectionReference, StoreCatalogReference
from web_app.serialization.dto import PaginationOutputDto, AuthorizedPaginationInputDto


@dataclass
class StoreCollectionResponseDto:
    collection_id: str
    reference: str
    display_name: str
    disabled: bool

    def serialize(self):
        return {
            'collection_id': self.collection_id,
            'reference': self.reference,
            'display_name': self.display_name,
            'disabled': self.disabled,
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
            'reference': self.reference,
            'display_name': self.display_name,
            'system': self.system,
            'disabled': self.disabled,
            'collections': [c.serialize() for c in self.collections]
        }


@dataclass
class StoreProductResponseDto:
    collection_id: str
    reference: str
    display_name: str

    def serialize(self):
        return {
            'display_name': self.display_name
        }


class FetchAllStoreCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreCatalogResponseDto]:
        pass


class FetchAllStoreCollectionsQuery(abc.ABC):
    @abc.abstractmethod
    def query(
            self,
            catalog_reference: str,
            dto: AuthorizedPaginationInputDto
    ) -> PaginationOutputDto[StoreCollectionResponseDto]:
        pass


class FetchAllStoreProductsQuery(abc.ABC):
    @abc.abstractmethod
    def query(
            self,
            collection_reference: StoreCollectionReference,
            catalog_reference: StoreCatalogReference,
            dto: AuthorizedPaginationInputDto
    ) -> PaginationOutputDto[StoreProductResponseDto]:
        pass
