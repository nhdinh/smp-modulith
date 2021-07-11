#!/usr/bin/env python
# -*- coding: utf-8 -*-
import email_validator
from sqlalchemy import select, and_
from sqlalchemy.engine import Connection

from inventory.domain.entities.warehouse import Warehouse, WarehouseId
from store.adapter.store_db import store_warehouse_table, store_table, store_managers_table, store_user_table
from store.domain.entities.store import Store
from store.domain.entities.store_owner import StoreUser


def sql_get_warehouse_id_by_owner(warehouse_owner: str, conn: Connection, active_only: bool = True) -> WarehouseId:
    try:
        email_validator.validate_email(warehouse_owner)

        # q = select(Warehouse.warehouse_id) \
        #     .join(Store).join(StoreUser) \
        #     .where(StoreUser.email == warehouse_owner)
        # if active_only:
        #     q = q.where(and_(Store.disabled == False, Warehouse.disabled == False))
        # warehouse_id = conn.scalar(q)

        q = select(store_warehouse_table.c.warehouse_id) \
            .join(store_managers_table, store_warehouse_table.c.store_id == store_managers_table.c.store_id) \
            .join(store_user_table, store_managers_table.c.user_id == store_user_table.c.user_id) \
            .where(store_user_table.c.email == warehouse_owner)

        if active_only:
            q = q.where(and_(store_warehouse_table.c.disabled == False))

        warehouse_id = conn.scalar(q)

        return warehouse_id
    except Exception as exc:
        raise exc
