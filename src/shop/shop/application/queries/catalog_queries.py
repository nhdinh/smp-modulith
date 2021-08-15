#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from shop.domain.dtos.catalog_dtos import ShopCatalogResponseDto
from shop.domain.dtos.product_dtos import ShopProductCompactedDto
from shop.domain.entities.value_objects import ShopCatalogId
from web_app.serialization.dto import BasePaginationAuthorizedRequest, PaginationTypedResponse, \
    BaseAuthorizedShopUserRequest, SimpleListTypedResponse


@dataclass
class ListShopCatalogsRequest(BasePaginationAuthorizedRequest):
    ...


@dataclass
class ListAllShopCatalogRequest(BaseAuthorizedShopUserRequest):
    ...


class ListShopCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopCatalogsRequest) -> PaginationTypedResponse[ShopCatalogResponseDto]:
        raise NotImplementedError


class ListAllShopCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListAllShopCatalogRequest) -> SimpleListTypedResponse[ShopCatalogResponseDto]:
        raise NotImplementedError


@dataclass
class ListShopProductsByCatalogRequest(BasePaginationAuthorizedRequest):
    catalog_id: ShopCatalogId = ''
    use_view_cache: bool = True


class ListShopProductsByCatalogQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopProductsByCatalogRequest) -> PaginationTypedResponse[ShopProductCompactedDto]:
        raise NotImplementedError
