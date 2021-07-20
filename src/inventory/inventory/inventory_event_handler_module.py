#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from foundation import AsyncEventHandlerProvider, AsyncHandler
from foundation.domain_events.identity_events import ShopAdminCreatedEvent
from foundation.domain_events.shop_events import ShopProductCreatedEvent
from foundation.events import EventHandlerProvider, EveryModuleMustCatchThisEvent, Handler

from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from inventory.inventory_handler_facade import (
    CreateWarehouseUponShopCreatedHandler,
    Inventory_CatchAllEventHandler,
    InventoryHandlerFacade,
    ShopProductCreatedEventHandler,
)


class InventoryEventHandlerModule(injector.Module):
    @injector.provider
    def facade(self, uow: InventoryUnitOfWork) -> InventoryHandlerFacade:
        return InventoryHandlerFacade(uow=uow)

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

        binder.multibind(
            AsyncHandler[ShopProductCreatedEvent],
            to=AsyncEventHandlerProvider(ShopProductCreatedEventHandler))
