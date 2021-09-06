#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from shop.domain.dtos.catalog_dtos import ShopCatalogDto
from shop.domain.dtos.collection_dtos import ShopCollectionDto, ShopCollectionShortDto
from shop.domain.dtos.product_dtos import ShopProductDto
from shop.domain.entities.value_objects import ShopCatalogId
from web_app.serialization.dto import BasePaginationAuthorizedRequest, PaginationTypedResponse, \
    BaseAuthorizedShopUserRequest, SimpleListTypedResponse, GeneralHashDto


class ShopCatalogOrderOptions(Enum):
    CREATED_DATE = 'CREATED_DATE'
    UPDATED_DATE = 'UPDATED_DATE'
    PRODUCT_COUNT = 'PRODUCT_COUNT'
    COLLECTION_COUNT = 'COLLECTION_COUNT'
    DEFAULT = 'DEFAULT'


@dataclass
class ListShopCatalogsRequest(BasePaginationAuthorizedRequest):
    order_by: Optional[ShopCatalogOrderOptions] = ShopCatalogOrderOptions.CREATED_DATE
    order_direction_descending: Optional[bool] = True
    display_deleted: Optional[bool] = False
    display_disabled: Optional[bool] = False


@dataclass
class ListActiveShopCatalogsRequest(BaseAuthorizedShopUserRequest):
    ...


class ListShopCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopCatalogsRequest) -> PaginationTypedResponse[ShopCatalogDto]:
        raise NotImplementedError


class ListActiveShopCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListActiveShopCatalogsRequest) -> SimpleListTypedResponse[ShopCatalogDto]:
        raise NotImplementedError


@dataclass
class ListShopProductsByCatalogRequest(BasePaginationAuthorizedRequest):
    catalog_id: ShopCatalogId = ''
    use_view_cache: bool = True


class ListShopProductsByCatalogQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopProductsByCatalogRequest) -> PaginationTypedResponse[ShopProductDto]:
        raise NotImplementedError


@dataclass
class ListShopCollectionsByCatalogRequest(BasePaginationAuthorizedRequest):
    catalog_id: ShopCatalogId = ''
    use_view_cache: bool = True


class ListShopCollectionsByCatalogQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopCollectionsByCatalogRequest) -> PaginationTypedResponse[ShopCollectionDto]:
        raise NotImplementedError


@dataclass
class ListActiveShopCollectionsByCatalogRequest(BaseAuthorizedShopUserRequest):
    catalog_id: ShopCatalogId = ''


class ListActiveShopCollectionsByCatalogQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListActiveShopCollectionsByCatalogRequest) -> SimpleListTypedResponse[ShopCollectionShortDto]:
        raise NotImplementedError


@dataclass
class GetCollectionCacheHashRequest(BaseAuthorizedShopUserRequest):
    catalog_id: ShopCatalogId


class GetCollectionCacheHashQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: GetCollectionCacheHashRequest) -> GeneralHashDto:

        raise NotImplementedError
