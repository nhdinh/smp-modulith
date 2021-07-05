#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import List

from store.application.queries.response_dtos import StoreCollectionResponseDto, \
    StoreCatalogResponseDto, StoreProductShortResponseDto, StoreProductResponseDto, StoreInfoResponseDto, \
    StoreWarehouseResponseDto, StoreAddressResponseDto, StoreSupplierResponseDto
from store.domain.entities.store_catalog import StoreCatalogReference, StoreCatalogId
from store.domain.entities.store_collection import StoreCollectionReference
from store.domain.entities.store_product import StoreProductId, StoreProductReference
from web_app.serialization.dto import PaginationOutputDto, AuthorizedPaginationInputDto


class ListStoreCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreCatalogResponseDto]:
        pass


class ListStoreCollectionsQuery(abc.ABC):
    @abc.abstractmethod
    def query(
            self,
            catalog_reference: str,
            dto: AuthorizedPaginationInputDto
    ) -> PaginationOutputDto[StoreCollectionResponseDto]:
        pass


class ListProductsFromCollectionQuery(abc.ABC):
    @abc.abstractmethod
    def query(
            self,
            collection_reference: StoreCollectionReference,
            catalog_reference: StoreCatalogReference,
            dto: AuthorizedPaginationInputDto
    ) -> PaginationOutputDto[StoreProductShortResponseDto]:
        pass


class ListProductsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, owner_email: str,
              catalog_reference: StoreCatalogReference,
              collection_reference: StoreCollectionReference,
              product_reference: StoreProductReference) -> StoreProductResponseDto:
        pass


class GetProductByIdQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, owner_email: str, product_id: StoreProductId) -> StoreProductResponseDto:
        pass


class ListStoreProductsByCatalogQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, catalog_id: StoreCatalogId, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[
        StoreProductShortResponseDto]:
        pass


class ListStoreProductsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreProductShortResponseDto]:
        pass


class ListStoreSettingsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, store_of: str) -> StoreInfoResponseDto:
        pass


class CountStoreOwnerByEmailQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, email: str) -> int:
        pass


class ListStoreWarehousesQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, warehouse_owner: str) -> List[StoreWarehouseResponseDto]:
        pass


class ListStoreAddressesQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, store_owner: str) -> List[StoreAddressResponseDto]:
        pass


class ListStoreSuppliersQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreSupplierResponseDto]:
        pass
