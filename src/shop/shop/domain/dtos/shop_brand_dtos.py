#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from typing import Union

from sqlalchemy.engine.row import RowProxy

from shop.domain.entities.value_objects import ShopBrandId, GenericShopItemStatus


@dataclass
class ShopBrandCompactedDto:
    brand_id: ShopBrandId
    brand_name: str
    logo: str
    status: GenericShopItemStatus
    product_count: int
    created_at: datetime
    updated_at: datetime

    def serialize(self):
        return self.__dict__


@dataclass
class StoreProductBrandDto:
    brand_id: ShopBrandId
    brand_name: str
    logo: str
    status: GenericShopItemStatus
    product_count: int
    created_at: datetime
    updated_at: datetime

    def serialize(self):
        return self.__dict__


def _row_to_brand_dto(row: RowProxy) -> Union[ShopBrandCompactedDto, StoreProductBrandDto]:
    return StoreProductBrandDto(
        brand_id=row.brand_id,
        brand_name=row.brand_name,
        logo=row.logo,
        status=row.status,
        product_count=row.product_count,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
