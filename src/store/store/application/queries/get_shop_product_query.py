#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.queries.dtos.store_product_dto import StoreProductDto
from store.domain.entities.value_objects import ShopProductId
from web_app.serialization.dto import BaseShopInputDto


@dataclass
class GetShopProductRequest(BaseShopInputDto):
    product_id: ShopProductId


class GetShopProductQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, dto:GetShopProductRequest, from_cache: bool = True) -> StoreProductDto:
        pass
