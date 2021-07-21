#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from typing import List

from shop.domain.dtos.product_dtos import ShopProductDto, ShopProductCompactedDto
from shop.domain.entities.value_objects import ShopProductId
from web_app.serialization.dto import BaseShopInputDto, AuthorizedPaginationInputDto


@dataclass
class GetShopProductRequest(BaseShopInputDto):
    product_id: ShopProductId


class GetShopProductQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: GetShopProductRequest, from_cache: bool = True) -> ShopProductDto:
        raise NotImplementedError


@dataclass
class ListShopProductsRequest(AuthorizedPaginationInputDto):
    pass


class ListShopProductsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopProductsRequest, use_view_cache: bool = True) -> List[ShopProductCompactedDto]:
        raise NotImplementedError
