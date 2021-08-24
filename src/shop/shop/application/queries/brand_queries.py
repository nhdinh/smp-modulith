#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from shop.domain.dtos.shop_brand_dtos import ShopBrandCompactedDto
from web_app.serialization.dto import SimpleListTypedResponse, \
    BasePaginationAuthorizedRequest


class BrandOrderBy(Enum):
    NAME = 'NAME'
    PRODUCT_COUNT = 'PRODUCT_COUNT'
    CREATED_DATE = 'CREATED_DATE'


@dataclass()
class ListShopBrandsRequest(BasePaginationAuthorizedRequest):
    order_by: Optional[BrandOrderBy] = BrandOrderBy.CREATED_DATE
    order_direction_descending: bool = True  # DESC,
    use_view_cache: bool = True
    display_disabled: bool = True
    display_deleted: bool = False


class ListShopBrandsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: ListShopBrandsRequest) -> SimpleListTypedResponse[ShopBrandCompactedDto]:
        raise NotImplementedError
