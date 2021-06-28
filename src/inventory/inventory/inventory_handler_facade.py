#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy import insert
from sqlalchemy.engine import Connection
from typing import List

from foundation.logger import logger
from store.domain.entities.value_objects import StoreId, StoreProductId
from store.domain.events.store_product_created_event import StoreProductCreatedEvent


class InventoryHandlerFacade:
    def __init__(self, connection: Connection):
        self._conn = connection

    def update_inventory_first_stock(self, store_id: StoreId, product_id: StoreProductId, default_unit: str,
                                     units: List[str], first_stocks: List[int]):
        # query = insert(inventory_stock_balance_table).values(**{
        #     'store_id': store_id,
        #     'product_id': product_id,
        # })

        # TODO: update data into first stock database
        for stock in first_stocks:
            logger.info(f"TODO: add {stock} number into first stock database of {product_id}")


class StoreProductCreatedEventHandler:
    @injector.inject
    def __init__(self, facade: InventoryHandlerFacade) -> None:
        self._f = facade

    def __call__(self, event: StoreProductCreatedEvent) -> None:
        self._f.update_inventory_first_stock(
            event.store_id,
            event.product_id,
            event.default_unit,
            event.units,
            event.first_stocks
        )
