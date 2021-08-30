#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime

from shop.domain.entities.value_objects import ShopBrandId, GenericShopItemStatus


@dataclass
class ShopBrandShortDto:
    brand_id: ShopBrandId
    brand_name: str
    logo: str

    def serialize(self):
        return self.__dict__


@dataclass
class ShopBrandDto(ShopBrandShortDto):
    status: GenericShopItemStatus
    product_count: int
    created_at: datetime
    updated_at: datetime

    def serialize(self):
        return self.__dict__
