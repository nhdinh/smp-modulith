#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from sqlalchemy.engine.row import RowProxy


@dataclass
class StoreSupplierDto:
    supplier_id: str
    supplier_name: str
    contact_name: str
    contact_phone: str
    disabled: bool

    def serialize(self):
        return self.__dict__


def _row_to_supplier_dto(row: RowProxy) -> StoreSupplierDto:
    return StoreSupplierDto(
        supplier_id=row.supplier_id,
        supplier_name=row.supplier_name,
        contact_name=row.contact_name,
        contact_phone=row.contact_phone,
        disabled=row.disabled
    )