#!/usr/bin/env python
# -*- coding: utf-8 -*-
import email_validator
from sqlalchemy import select, and_
from sqlalchemy.engine import Connection

from inventory.domain.entities.warehouse import Warehouse, WarehouseId
from store.adapter.shop_db import shop_warehouse_table, shop_table, shop_users_table, system_user_table
from store.domain.entities.shop import Shop


def sql_get_warehouse_id_by_owner(warehouse_owner: str, conn: Connection, active_only: bool = True) -> WarehouseId:
    try:
        email_validator.validate_email(warehouse_owner)

        # q = select(Warehouse.warehouse_id) \
        #     .join(Store).join(StoreUser) \
        #     .where(StoreUser.email == warehouse_owner)
        # if active_only:
        #     q = q.where(and_(Store.disabled == False, Warehouse.disabled == False))
        # warehouse_id = conn.scalar(q)

        q = select(shop_warehouse_table.c.warehouse_id) \
            .join(shop_users_table, shop_warehouse_table.c.shop_id == shop_users_table.c.shop_id) \
            .join(system_user_table, shop_users_table.c.user_id == system_user_table.c.user_id) \
            .where(system_user_table.c.email == warehouse_owner)

        if active_only:
            q = q.where(and_(shop_warehouse_table.c.disabled == False))

        warehouse_id = conn.scalar(q)

        return warehouse_id
    except Exception as exc:
        raise exc
