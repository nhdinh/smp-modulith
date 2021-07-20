#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from shop.domain.dtos.product_dtos import ShopProductDto
from shop.domain.entities.value_objects import ShopProductId
from web_app.serialization.dto import BaseShopInputDto


@dataclass
class GetShopProductRequest(BaseShopInputDto):
    product_id: ShopProductId


class GetShopProductQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto: GetShopProductRequest, from_cache: bool = True) -> ShopProductDto:
        pass
