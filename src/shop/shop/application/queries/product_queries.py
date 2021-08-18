#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from shop.domain.dtos.product_dtos import ShopProductDto, ShopProductCompactedDto, ShopProductPriceDto
from shop.domain.dtos.product_unit_dtos import ShopProductUnitDto
from shop.domain.dtos.supplier_dtos import ShopSupplierDto
from shop.domain.entities.value_objects import ShopProductId, ShopSupplierId
from web_app.serialization.dto import BaseAuthorizedShopUserRequest, BasePaginationAuthorizedRequest, \
  SimpleListTypedResponse, PaginationTypedResponse


@dataclass
class GetShopProductRequest(BaseAuthorizedShopUserRequest):
  product_id: ShopProductId


class GetShopProductQuery(abc.ABC):
  @abc.abstractmethod
  def query(self, dto: GetShopProductRequest) -> ShopProductDto:
    raise NotImplementedError


class ProductOrderBy(Enum):
  TITLE = "TITLE"
  CATALOG_TITLE = "CATALOG_TITLE",
  BRAND_NAME = "BRAND_NAME",
  CREATED_DATE = "CREATED_DATE",
  CURRENT_STOCK = "STOCKING_QUANTITY"


@dataclass
class ListShopProductsRequest(BasePaginationAuthorizedRequest):
  order_by: Optional[ProductOrderBy] = ProductOrderBy.CURRENT_STOCK
  order_direction_descending: bool = True  # DESC,
  use_view_cache: bool = True


class ListShopProductsQuery(abc.ABC):
  @abc.abstractmethod
  def query(self, dto: ListShopProductsRequest) -> PaginationTypedResponse[ShopProductCompactedDto]:
    raise NotImplementedError


@dataclass
class ListShopProductPurchasePricesRequest(BaseAuthorizedShopUserRequest):
  product_id: ShopProductId
  group_by_supplier: Optional[bool] = True


class ListShopProductPurchasePricesQuery(abc.ABC):
  @abc.abstractmethod
  def query(self, dto: ListShopProductPurchasePricesRequest) -> SimpleListTypedResponse[ShopProductPriceDto]:
    raise NotImplementedError


@dataclass
class ListUnitsByShopProductRequest(BaseAuthorizedShopUserRequest):
  product_id: ShopProductId


class ListUnitsByShopProductQuery(abc.ABC):
  @abc.abstractmethod
  def query(self, dto: ListUnitsByShopProductRequest) -> SimpleListTypedResponse[ShopProductUnitDto]:
    raise NotImplementedError


@dataclass
class ListShopSuppliersByProductRequest(BaseAuthorizedShopUserRequest):
  product_id: ShopProductId


class ListShopSuppliersByProductQuery(abc.ABC):
  @abc.abstractmethod
  def query(self, dto: ListShopSuppliersByProductRequest) -> SimpleListTypedResponse[ShopSupplierDto]:
    raise NotImplementedError


@dataclass
class GetShopProductPurchasePriceRequest(BaseAuthorizedShopUserRequest):
  product_id: ShopProductId
  supplier_id: ShopSupplierId
  unit: str


class GetShopProductPurchasePriceQuery(abc.ABC):
  @abc.abstractmethod
  def query(self, dto: GetShopProductPurchasePriceRequest) -> ShopProductPriceDto:
    raise NotImplementedError


@dataclass()
class GetShopProductLowestPurchasePriceRequest(BaseAuthorizedShopUserRequest):
  product_id: ShopProductId
  unit: str


class GetShopProductLowestPurchasePriceQuery(abc.ABC):
  @abc.abstractmethod
  def query(self, dto: GetShopProductLowestPurchasePriceRequest) -> ShopProductPriceDto:
    raise NotImplementedError
