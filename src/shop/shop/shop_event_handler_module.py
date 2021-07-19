#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from foundation.domain_events.identity_events import UserCreatedEvent
from foundation.domain_events.inventory_events import WarehouseCreatedEvent
from foundation.events import AsyncHandler, EveryModuleMustCatchThisEvent, AsyncEventHandlerProvider
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.shop_handler_facade import ShopHandlerFacade, Shop_CatchAllEventHandler, \
    CreateShopAndUpdateRegistrationWhileUserCreatedEventHandler, UpdateShopWhileWarehouseCreatedEventHandler


class ShopEventHandlerModule(injector.Module):
    @injector.provider
    def facade(self, uow: ShopUnitOfWork) -> ShopHandlerFacade:
        return ShopHandlerFacade(uow)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[EveryModuleMustCatchThisEvent],
                         to=AsyncEventHandlerProvider(Shop_CatchAllEventHandler))

        binder.multibind(AsyncHandler[UserCreatedEvent],
                         to=AsyncEventHandlerProvider(CreateShopAndUpdateRegistrationWhileUserCreatedEventHandler))

        binder.multibind(AsyncHandler[WarehouseCreatedEvent],
                         to=AsyncEventHandlerProvider(UpdateShopWhileWarehouseCreatedEventHandler))
