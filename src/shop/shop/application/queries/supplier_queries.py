#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from marshmallow import fields

from shop.adapter.id_generators import SHOP_SUPPLIER_ID_PREFIX
from shop.domain.dtos.product_dtos import ShopProductCompactedDto
from shop.domain.dtos.supplier_dtos import StoreSupplierResponseDto
from shop.domain.entities.value_objects import ShopSupplierId
from web_app.serialization.dto import (
    AuthorizedPaginationInputDto,
    BaseShopInputDto,
    PaginationInputDto,
    PaginationOutputDto,
)


@dataclass
class ListShopSuppliersRequest(PaginationInputDto, BaseShopInputDto):
    ...


class ListShopSuppliersQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopSuppliersRequest) -> PaginationOutputDto[StoreSupplierResponseDto]:
        pass


@dataclass
class ListShopProductsBySupplierRequest(PaginationInputDto, BaseShopInputDto):
    supplier_id: ShopSupplierId = fields.Str(required=True, validate=lambda x: x.startswith(SHOP_SUPPLIER_ID_PREFIX))


class ListShopProductsBySupplierQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopProductsBySupplierRequest) -> PaginationOutputDto[ShopProductCompactedDto]:
        pass
