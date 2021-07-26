#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from sqlalchemy.engine.row import RowProxy
from typing import List

from shop.domain.entities.value_objects import ShopSupplierId, GenericShopItemStatus


@dataclass
class SupplierContactDto:
    contact_name: str
    contact_phone: str
    contact_status: GenericShopItemStatus

    def serialize(self):
        return self.__dict__


@dataclass
class ShopSupplierDto:
    supplier_id: ShopSupplierId
    supplier_name: str
    contacts: List[SupplierContactDto]
    supplier_status: GenericShopItemStatus

    def serialize(self):
        return self.__dict__


def _row_to_supplier_contact_dto(row: RowProxy):
    return SupplierContactDto(
        contact_name=row.contact_name,
        contact_phone=row.contact_phone,
        contact_status=row.contact_status,
    )


def _row_to_supplier_dto(row: RowProxy, contact_rows: List[RowProxy] = []) -> ShopSupplierDto:
    return ShopSupplierDto(
        supplier_id=row.supplier_id,
        supplier_name=row.supplier_name,
        contacts=[_row_to_supplier_contact_dto(cr) for cr in contact_rows] if contact_rows else [],
        supplier_status=row.supplier_status
    )
