#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from foundation.domain_events.identity_events import ShopAdminCreatedEvent
from foundation.domain_events.inventory_events import WarehouseCreatedEvent
from foundation.domain_events.shop_events import ShopCreatedEvent, ShopProductCreatedEvent, ShopProductUpdatedEvent
from foundation.events import (
    AsyncEventHandlerProvider,
    AsyncHandler,
    EventHandlerProvider,
    EveryModuleMustCatchThisEvent,
    Handler,
)

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.shop_handler_facade import (
    AddWarehouseToShopUponWarehouseCreatedHandler,
    CreateDefaultCatalogUponShopCreatedHandler,
    CreateShopAndUpdateRegistrationUponUserCreatedHandler,
    GenerateViewCacheUponProductModificationHandler,
    Shop_CatchAllEventHandler,
    ShopHandlerFacade,
)


class ShopEventHandlerModule(injector.Module):
    @injector.provider
    def facade(self, uow: ShopUnitOfWork) -> ShopHandlerFacade:
        return ShopHandlerFacade(uow)

    def configure(self, binder: injector.Binder) -> None:
        self._configure_handler_bindings(binder=binder)
        self._configure_async_handler_bindings(binder=binder)

    def _configure_handler_bindings(self, binder: injector.Binder) -> None:
        # Handle Shop creation upon User Created (on ShopConfirmation)
        binder.multibind(
            Handler[ShopAdminCreatedEvent],
            to=EventHandlerProvider(CreateShopAndUpdateRegistrationUponUserCreatedHandler))

        # Handle Warehouse added into shop's warehouses list upon new Warehouse creation
        binder.multibind(
            Handler[WarehouseCreatedEvent],
            to=EventHandlerProvider(AddWarehouseToShopUponWarehouseCreatedHandler))

    def _configure_async_handler_bindings(self, binder: injector.Binder) -> None:
        binder.multibind(
            AsyncHandler[EveryModuleMustCatchThisEvent],
            to=AsyncEventHandlerProvider(Shop_CatchAllEventHandler))

        # Handle Default Catalog creation upon New Shop Created
        binder.multibind(
            AsyncHandler[ShopCreatedEvent],
            to=AsyncEventHandlerProvider(CreateDefaultCatalogUponShopCreatedHandler))

        # Handle Adding a data cache of new Product upon its creation
        binder.multibind(
            AsyncHandler[ShopProductUpdatedEvent],
            to=AsyncEventHandlerProvider(GenerateViewCacheUponProductModificationHandler))
        binder.multibind(
            AsyncHandler[ShopProductCreatedEvent],
            to=AsyncEventHandlerProvider(GenerateViewCacheUponProductModificationHandler))
