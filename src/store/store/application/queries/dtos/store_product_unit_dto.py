#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from typing import Union

from sqlalchemy.engine.row import RowProxy


@dataclass
class StoreProductUnitCompactedDto:
    unit_name: str
    referenced_unit_name: str
    conversion_factor: float
    is_default: bool

    def serialize(self):
        return self.__dict__


@dataclass
class StoreProductUnitDto(StoreProductUnitCompactedDto):
    is_disabled: bool
    created_at: datetime
    # updated_at: datetime


def _row_to_unit_dto(row: RowProxy, compacted: bool = True) -> Union[StoreProductUnitCompactedDto, StoreProductUnitDto]:
    if compacted:
        return StoreProductUnitCompactedDto(
            unit_name=row.unit_name,
            referenced_unit_name=row.referenced_unit_name,
            conversion_factor=row.conversion_factor,
            is_default=row.default
        )
    else:
        return StoreProductUnitDto(
            unit_name=row.unit_name,
            is_default=row.default,
            is_disabled=row.disabled,
            referenced_unit_name=row.referenced_unit_name,
            conversion_factor=row.conversion_factor,
            created_at=row.created_at,
            # updated_at=row.updated_at,
        )
