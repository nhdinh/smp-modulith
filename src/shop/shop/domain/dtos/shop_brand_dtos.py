#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from typing import Union

from sqlalchemy.engine.row import RowProxy

from shop.domain.entities.value_objects import ShopBrandId


@dataclass
class ShopBrandCompactedDto:
    brand_id: ShopBrandId
    brand_name: str
    logo: str

    def serialize(self):
        return self.__dict__


@dataclass
class StoreProductBrandDto(ShopBrandCompactedDto):
    created_at: datetime
    updated_at: datetime


def _row_to_brand_dto(
        row: RowProxy, compacted: bool = True
) -> Union[ShopBrandCompactedDto, StoreProductBrandDto]:
    if compacted:
        return ShopBrandCompactedDto(
            brand_id=row.brand_id,
            brand_name=row.brand_name,
            logo=row.logo,
        )
    else:
        return StoreProductBrandDto(
            brand_id=row.brand_id,
            brand_name=row.brand_name,
            logo=row.logo,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
