#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from marshmallow import fields

from shop.adapter.id_generators import SHOP_SUPPLIER_ID_PREFIX
from shop.domain.dtos.product_dtos import ShopProductCompactedDto
from shop.domain.dtos.supplier_dtos import ShopSupplierDto
from shop.domain.entities.value_objects import ShopSupplierId
from web_app.serialization.dto import (
    BaseAuthorizedShopUserRequest,
    BasePaginationRequest,
    PaginationTypedResponse,
)


@dataclass
class ListShopSuppliersRequest(BasePaginationRequest, BaseAuthorizedShopUserRequest):
    ...


class ListShopSuppliersQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopSuppliersRequest) -> PaginationTypedResponse[ShopSupplierDto]:
        raise NotImplementedError


@dataclass
class ListShopProductsBySupplierRequest(BasePaginationRequest, BaseAuthorizedShopUserRequest):
    supplier_id: ShopSupplierId = fields.Str(required=True, validate=lambda x: x.startswith(SHOP_SUPPLIER_ID_PREFIX))


class ListShopProductsBySupplierQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopProductsBySupplierRequest) -> PaginationTypedResponse[ShopProductCompactedDto]:
        raise NotImplementedError
