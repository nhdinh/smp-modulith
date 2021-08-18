#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import injector
from sqlalchemy import insert, update, and_
from sqlalchemy.engine import Connection

from foundation.events import EveryModuleMustCatchThisEvent, EventBus, new_event_id
from foundation.logger import logger
from identity.domain.events import ShopAdminCreatedEvent
from inventory.adapter.id_generators import generate_warehouse_id
from inventory.adapter.inventory_db import warehouse_table, warehouse_users_table
from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from inventory.domain.entities.value_objects import WarehouseStatus, WarehouseUserType, GenericWarehouseItemStatus, \
    WarehouseId
from inventory.domain.entities.warehouse import Warehouse
from inventory.domain.events import PendingWarehouseCreatedEvent


class InventoryHandlerFacade:
    def __init__(self, uow: InventoryUnitOfWork, conn: Connection, event_bus: EventBus):
        self._uow = uow
        self._conn = conn
        self._event_bus = event_bus

    def create_warehouse(self, user_id: str, email: str, user_created_at: datetime):
        with self._uow as uow:  # type:InventoryUnitOfWork
            try:
                any_warehouse = uow.inventory.get_warehouse_by_admin_id(user_id=user_id)
                if any_warehouse:
                    logger.debug(
                        f'Warehouse and WarehouseAdmin both created but ShopAdminCreatedEvent emitted. WarehouseId={any_warehouse.warehouse_id}. AdminId={user_id}')
                    return

                warehouse_admin = Warehouse.generate_warehouse_admin(user_id=user_id, email=email)
                warehouse = Warehouse.create(warehouse_admin=warehouse_admin)

                uow.inventory.save(warehouse)

                uow.commit()
            except Exception as exc:
                raise exc

    # def update_inventory_first_stock(
    #         self,
    #         store_id: ShopId,
    #         product_id: ShopProductId,
    #         default_unit: str,
    #         units: List[str],
    #         first_stocks: List[int]
    # ) -> None:
    #     values_to_insert = []
    #     for cnt in range(0, len(units)):
    #         if first_stocks[cnt] != 0:
    #             values_to_insert.append({
    #                 'product_id': product_id,
    #                 'unit': units[cnt],
    #                 'stocking_quantity': first_stocks[cnt]
    #             })
    #
    #     query = insert(inventory_product_balance_table).values(values_to_insert)
    #     self._conn.execute(query)

    def update_first_stocking(self, product_id, shop_id, units, first_stocking):
        pass

    def create_pending_warehouse(self, user_id: str, warehouse_name: str, procman_id: str):
        warehouse_id = generate_warehouse_id()
        insertion = insert(warehouse_table).values(warehouse_id=warehouse_id, name=warehouse_name, default=True,
                                                   status=WarehouseStatus.PENDING_CREATION)
        self._conn.execute(insertion)

        insertion = insert(warehouse_users_table).values(warehouse_id=warehouse_id, user_id=user_id,
                                                         warehouse_role=WarehouseUserType.ADMIN,
                                                         status=GenericWarehouseItemStatus.PENDING_CREATION)
        self._conn.execute(insertion)

        self._event_bus.post(PendingWarehouseCreatedEvent(event_id=new_event_id(),
                                                          procman_id=procman_id,
                                                          warehouse_id=warehouse_id))

    def activate_pending_warehouse(self, warehouse_id: WarehouseId, user_id: str):
        modification = update(warehouse_table).values(status=WarehouseStatus.NORMAL).where(
            warehouse_table.c.warehouse_id == warehouse_id
        )
        self._conn.execute(modification)

        modification = update(warehouse_users_table).values(status=GenericWarehouseItemStatus.NORMAL).where(
            and_(warehouse_users_table.c.user_id == user_id, warehouse_users_table.c.warehouse_id == warehouse_id))
        self._conn.execute(modification)

    def update_warehouse_user_data(self, user_id: str, email: str):
        q = update(warehouse_users_table).where(warehouse_users_table.c.user_id == user_id).values(email=email)
        self._conn.execute(q)


class CreateWarehouseUponShopCreatedHandler:
    @injector.inject
    def __init__(self, facade: InventoryHandlerFacade) -> None:
        self._f = facade

    def __call__(self, event: ShopAdminCreatedEvent):
        try:
            event_id = event.event_id
            user_id = event.user_id
            email = event.email
            mobile = event.mobile
            created_at = event.created_at

            self._f.create_warehouse(
                user_id=user_id,
                email=email,
                user_created_at=created_at
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
