#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from sqlalchemy.engine.row import RowProxy

from shop.domain.entities.value_objects import ShopSupplierId


@dataclass
class StoreSupplierResponseDto:
    supplier_id: ShopSupplierId
    supplier_name: str
    contact_name: str
    contact_phone: str
    supplier_status: bool

    def serialize(self):
        return self.__dict__


def _row_to_supplier_dto(row: RowProxy) -> StoreSupplierResponseDto:
    return StoreSupplierResponseDto(
        supplier_id=row.supplier_id,
        supplier_name=row.supplier_name,
        contact_name=row.contact_name,
        contact_phone=row.contact_phone,
        supplier_status=row.supplier_status
    )