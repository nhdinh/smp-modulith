#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List

import injector
from sqlalchemy import insert
from sqlalchemy.engine import Connection

from inventory.adapter.inventory_db import inventory_product_balance_table
# from inventory.adapter.inventory_db import inventory_product_balance_table
from store.domain.entities.store import StoreId
from store.domain.entities.store_product import StoreProductId
from store.domain.events.store_product_created_event import StoreProductCreatedEvent


class InventoryHandlerFacade:
    def __init__(self, connection: Connection):
        self._conn = connection

    def update_inventory_first_stock(
            self,
            store_id: StoreId,
            product_id: StoreProductId,
            default_unit: str,
            units: List[str],
            first_stocks: List[int]
    ) -> None:
        values_to_insert = []
        for cnt in range(0, len(units)):
            if first_stocks[cnt] != 0:
                values_to_insert.append({
                    'product_id': product_id,
                    'unit': units[cnt],
                    'stocking_quantity': first_stocks[cnt]
                })

        query = insert(inventory_product_balance_table).values(values_to_insert)
        self._conn.execute(query)


class StoreProductCreatedEventHandler:
    @injector.inject
    def __init__(self, facade: InventoryHandlerFacade) -> None:
        self._f = facade

    def __call__(self, event: StoreProductCreatedEvent) -> None:
        pass
        # self._f.update_inventory_first_stock(
        #     event.store_id,
        #     event.product_id,
        #     event.default_unit,
        #     event.units,
        #     event.first_stocks
        # )
