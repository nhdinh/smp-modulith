#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from shop.domain.dtos.product_dtos import ShopProductCompactedDto
from shop.domain.dtos.supplier_dtos import StoreSupplierResponseDto
from shop.domain.entities.value_objects import ShopSupplierId
from web_app.serialization.dto import (
    AuthorizedPaginationInputDto,
    BaseShopInputDto,
    PaginationInputDto,
    PaginationOutputDto,
)


class ListShopSuppliersQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreSupplierResponseDto]:
        pass


@dataclass
class ListShopProductsBySupplierRequest(PaginationInputDto, BaseShopInputDto):
    supplier_id: ShopSupplierId = ''


class ListShopProductsBySupplierQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopProductsBySupplierRequest) -> PaginationOutputDto[ShopProductCompactedDto]:
        pass
