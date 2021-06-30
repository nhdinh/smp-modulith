#!/usr/bin/env python
# -*- coding: utf-8 -*-
import email_validator
from sqlalchemy import select, and_
from sqlalchemy.engine import Connection

from inventory.domain.entities.warehouse import Warehouse, WarehouseId
from store.domain.entities.store import Store
from store.domain.entities.store_owner import StoreOwner


def sql_get_warehouse_id_by_owner(warehouse_owner: str, conn: Connection, active_only: bool = True) -> WarehouseId:
    try:
        email_validator.validate_email(warehouse_owner)

        q = select([Warehouse.store_id]).join(Store) \
            .where(Store.owner_email == warehouse_owner)
        if active_only:
            q = q.where(and_(Store.disabled == False, Warehouse.disabled == False))

        warehouse_id = conn.scalar(q)

        if not warehouse_id:
            q = select(Warehouse.warehouse_id) \
                .join(Store).join(StoreOwner) \
                .where(StoreOwner.email == warehouse_owner)
            if active_only:
                q = q.where(and_(Store.disabled == False, Warehouse.disabled == False))
            warehouse_id = conn.scalar(q)

        return warehouse_id
    except Exception as exc:
        raise exc
