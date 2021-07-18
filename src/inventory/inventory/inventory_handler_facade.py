#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

import injector
from sqlalchemy import insert
from sqlalchemy.engine import Connection

from foundation.domain_events.shop_events import ShopCreatedEvent
from foundation.events import EveryModuleMustCatchThisEvent
from foundation.logger import logger
from inventory.adapter.id_generators import generate_warehouse_id
from inventory.adapter.inventory_db import inventory_product_balance_table
from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from inventory.domain.entities.warehouse import Warehouse
from store.domain.entities.value_objects import ShopId, ShopProductId
from store.domain.events.store_product_events import StoreProductCreatedEvent


class InventoryHandlerFacade:
    def __init__(self, connection: Connection, uow: InventoryUnitOfWork):
        self._conn = connection
        self._uow = uow

    def update_inventory_first_stock(
            self,
            store_id: ShopId,
            product_id: ShopProductId,
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

    def create_warehouse(self, shop_id: str, admin_id: str, admin_email: str, shop_created_at: datetime):
        with self._uow as uow:  # type:InventoryUnitOfWork
            try:
                warehouse = Warehouse(
                    warehouse_id=generate_warehouse_id(),
                    store_id=shop_id,
                    warehouse_owner=admin_email
                )

                uow.inventory.save(warehouse)

                uow.commit()
            except Exception as exc:
                raise exc


class StoreProductCreatedEventHandler:
    @injector.inject
    def __init__(self, facade: InventoryHandlerFacade) -> None:
        self._f = facade

    def __call__(self, event: StoreProductCreatedEvent) -> None:
        pass
        # self._f.update_inventory_first_stock(
        #     event.shop_id,
        #     event.product_id,
        #     event.default_unit,
        #     event.units,
        #     event.first_stocks
        # )


class ShopCreatedEventHandler:
    @injector.inject
    def __init__(self, facade: InventoryHandlerFacade) -> None:
        self._f = facade

    def __call__(self, event: ShopCreatedEvent):
        try:
            self._f.create_warehouse(
                event.shop_id,
                event.admin_id,
                event.admin_email,
                event.shop_created_at,
            )
        except Exception as exc:
            # do something
            pass


class Inventory_CatchAllEventHandler:
    @injector.inject
    def __init__(self):
        ...

    def __call__(self, event: EveryModuleMustCatchThisEvent):
        logger.debug(f'Inventory_{event.event_id}')
