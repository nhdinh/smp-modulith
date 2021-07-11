#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import select, func, distinct
from sqlalchemy.engine import Connection

from inventory.domain.entities.draft_purchase_order import DraftPurchaseOrder
from inventory.domain.entities.warehouse import WarehouseId, Warehouse


def sql_count_draft_purchase_orders_in_warehouse(warehouse_id: WarehouseId, conn: Connection) -> int:
    q = select([func.count(distinct(DraftPurchaseOrder.purchase_order_id))]). \
        join(Warehouse).where(Warehouse.warehouse_id == warehouse_id)

    return conn.scalar(q)
