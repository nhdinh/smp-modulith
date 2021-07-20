#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import distinct, func, select
from sqlalchemy.engine import Connection

from inventory.domain.entities.draft_purchase_order import DraftPurchaseOrder
from inventory.domain.entities.value_objects import WarehouseId
from inventory.domain.entities.warehouse import Warehouse


def sql_count_draft_purchase_orders_in_warehouse(warehouse_id: WarehouseId, conn: Connection) -> int:
    q = select([func.count(distinct(DraftPurchaseOrder.purchase_order_id))]). \
        join(Warehouse).where(Warehouse.warehouse_id == warehouse_id)

    return conn.scalar(q)
