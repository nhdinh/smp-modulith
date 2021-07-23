#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from shop.domain.dtos.product_dtos import ShopProductDto, ShopProductCompactedDto, ShopProductPriceDto
from shop.domain.entities.value_objects import ShopProductId
from web_app.serialization.dto import BaseAuthorizedShopUserRequest, BasePaginationAuthorizedRequest, SimpleListTypedResponse, PaginationTypedResponse


@dataclass
class GetShopProductRequest(BaseAuthorizedShopUserRequest):
    product_id: ShopProductId


class GetShopProductQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: GetShopProductRequest) -> ShopProductDto:
        raise NotImplementedError


@dataclass
class ListShopProductsRequest(BasePaginationAuthorizedRequest):
    use_view_cache: bool = True


class ListShopProductsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopProductsRequest) -> PaginationTypedResponse[ShopProductCompactedDto]:
        raise NotImplementedError


@dataclass
class ListShopProductPurchasePricesRequest(BaseAuthorizedShopUserRequest):
    product_id: ShopProductId
    group_by_unit: bool


class ListShopProductPurchasePricesQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopProductPurchasePricesRequest) -> SimpleListTypedResponse[ShopProductPriceDto]:
        raise NotImplementedError
