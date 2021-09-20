#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from typing import Union

from sqlalchemy.engine.row import RowProxy


@dataclass
class ShopProductUnitCompactedDto:
    unit_id: str
    unit_name: str
    referenced_unit_id: str
    conversion_factor: float
    is_default: bool

    def serialize(self):
        return self.__dict__


@dataclass
class ShopProductUnitDto(ShopProductUnitCompactedDto):
    is_disabled: bool
    created_at: datetime
    updated_at: datetime


def _row_to_unit_dto(row: RowProxy, compacted: bool = True) -> Union[ShopProductUnitCompactedDto, ShopProductUnitDto]:
    if compacted:
        return ShopProductUnitCompactedDto(
            unit_id=row.unit_id,
            unit_name=row.unit_name,
            referenced_unit_id=row.referenced_unit_id,
            conversion_factor=row.conversion_factor,
            is_default=row.default
        )
    else:
        return ShopProductUnitDto(
            unit_id=row.unit_id,
            unit_name=row.unit_name,
            is_default=row.default,
            is_disabled=row.disabled,
            referenced_unit_id=row.referenced_unit_id,
            conversion_factor=row.conversion_factor,
            created_at=row.created_at,
            # updated_at=row.updated_at,
        )
