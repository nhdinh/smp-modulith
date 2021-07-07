#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import List

from store.application.queries.dtos.store_catalog_dto import StoreCatalogResponseDto
from store.application.queries.dtos.store_collection_dto import StoreCollectionDto
from store.application.queries.dtos.store_product_dto import StoreProductCompactedDto, StoreProductDto
from store.application.queries.dtos.store_supplier_dto import StoreSupplierDto
from store.application.queries.response_dtos import StoreInfoResponseDto, \
    StoreWarehouseResponseDto, StoreAddressResponseDto
from store.domain.entities.store_product import StoreProductId
from store.domain.entities.value_objects import StoreCatalogId, StoreCollectionId
from web_app.serialization.dto import PaginationOutputDto, AuthorizedPaginationInputDto


class ListStoreCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreCatalogResponseDto]:
        pass


class ListStoreCollectionsQuery(abc.ABC):
    @abc.abstractmethod
    def query(
            self,
            catalog_id: StoreCatalogId,
            dto: AuthorizedPaginationInputDto
    ) -> PaginationOutputDto[StoreCollectionDto]:
        pass


class ListProductsFromCollectionQuery(abc.ABC):
    @abc.abstractmethod
    def query(
            self,
            collection_id: StoreCollectionId,
            catalog_id: StoreCatalogId,
            dto: AuthorizedPaginationInputDto
    ) -> PaginationOutputDto[StoreProductCompactedDto]:
        pass


class ListProductsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, owner_email: str, catalog_id: StoreCatalogId) -> StoreProductDto:
        pass


class GetProductByIdQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, owner_email: str, product_id: StoreProductId) -> StoreProductDto:
        pass


class ListStoreProductsByCatalogQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, catalog_id: StoreCatalogId, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[
        StoreProductCompactedDto]:
        pass


class ListStoreProductsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreProductCompactedDto]:
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
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreSupplierDto]:
        pass
