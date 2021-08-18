#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection

from foundation import AsyncEventHandlerProvider, AsyncHandler
from foundation.events import EventHandlerProvider, EveryModuleMustCatchThisEvent, Handler, EventBus
from identity.domain.events import ShopAdminCreatedEvent
from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from inventory.inventory_handler_facade import (
    CreateWarehouseUponShopCreatedHandler,
    Inventory_CatchAllEventHandler,
    InventoryHandlerFacade,
)


class InventoryEventHandlerModule(injector.Module):
    @injector.provider
    def facade(self, uow: InventoryUnitOfWork, conn: Connection, event_bus: EventBus) -> InventoryHandlerFacade:
        return InventoryHandlerFacade(uow=uow, conn=conn, event_bus=event_bus)

    def configure(self, binder: injector.Binder) -> None:
        self._configure_handler_bindings(binder=binder)
        self._configure_async_handler_bindings(binder=binder)

    def _configure_handler_bindings(self, binder: injector.Binder):
        # Handle Warehouse creation upon ShopAdminCreatedEvent
        binder.multibind(
            Handler[ShopAdminCreatedEvent],
            to=EventHandlerProvider(CreateWarehouseUponShopCreatedHandler))

    def _configure_async_handler_bindings(self, binder: injector.Binder):
        binder.multibind(
            AsyncHandler[EveryModuleMustCatchThisEvent],
            to=AsyncEventHandlerProvider(Inventory_CatchAllEventHandler))

        # binder.multibind(
        #     AsyncHandler[ShopProductCreatedEvent],
        #     to=AsyncEventHandlerProvider(ShopProductCreatedEventHandler))
