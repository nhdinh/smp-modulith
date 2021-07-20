#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import injector

from foundation.domain_events.identity_events import ShopAdminCreatedEvent
from foundation.domain_events.shop_events import ShopProductCreatedEvent
from foundation.events import EveryModuleMustCatchThisEvent
from foundation.logger import logger

from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from inventory.domain.entities.warehouse import Warehouse


class InventoryHandlerFacade:
    def __init__(self, uow: InventoryUnitOfWork):
        self._uow = uow

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


class ShopProductCreatedEventHandler:
    @injector.inject
    def __init__(self, facade: InventoryHandlerFacade) -> None:
        self._f = facade

    def __call__(self, event: ShopProductCreatedEvent) -> None:
        pass
        # self._f.update_inventory_first_stock(
        #     event.shop_id,
        #     event.product_id,
        #     event.default_unit,
        #     event.units,
        #     event.first_stocks
        # )


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
