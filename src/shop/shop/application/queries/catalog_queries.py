#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from shop.domain.dtos.catalog_dtos import ShopCatalogResponseDto
from shop.domain.dtos.product_dtos import ShopProductCompactedDto
from shop.domain.entities.value_objects import ShopCatalogId
from web_app.serialization.dto import AuthorizedPaginationInputDto, PaginationOutputDto


@dataclass
class ListShopCatalogsRequest(AuthorizedPaginationInputDto):
    ...


class ListShopCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopCatalogsRequest) -> PaginationOutputDto[ShopCatalogResponseDto]:
        raise NotImplementedError


@dataclass
class ListShopProductsByCatalogRequest(AuthorizedPaginationInputDto):
    catalog_id: ShopCatalogId = ''
    use_view_cache: bool = True


class ListShopProductsByCatalogQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopProductsByCatalogRequest) -> PaginationOutputDto[ShopProductCompactedDto]:
        raise NotImplementedError
