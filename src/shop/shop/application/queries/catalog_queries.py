#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc

from shop.domain.dtos.catalog_dtos import ShopCatalogResponseDto
from web_app.serialization.dto import AuthorizedPaginationInputDto, PaginationOutputDto


class ListShopCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[ShopCatalogResponseDto]:
        pass
