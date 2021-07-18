#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from foundation.domain_events.identity_events import UserCreatedEvent
from foundation.domain_events.inventory_events import WarehouseCreatedEvent
from foundation.events import EveryModuleMustCatchThisEvent, AsyncEventHandlerProvider, AsyncHandler
from store.application.services.store_unit_of_work import ShopUnitOfWork
from store.application.shop_handler_facade import ShopHandlerFacade, Shop_CatchAllEventHandler, \
    CreateShopAndUpdateRegistrationWhileUserCreatedEventHandler, UpdateShopWhileWarehouseCreatedEventHandler


class ShopEventHandlerModule(injector.Module):
    @injector.provider
    def facade(self, uow: ShopUnitOfWork) -> ShopHandlerFacade:
        return ShopHandlerFacade(uow=uow)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[EveryModuleMustCatchThisEvent],
                         to=AsyncEventHandlerProvider(Shop_CatchAllEventHandler))

        # binder.multibind(AsyncHandler[UserCreatedEvent],
        #                  to=AsyncEventHandlerProvider(CreateShopAndUpdateRegistrationWhileUserCreatedEventHandler))

        binder.multibind(AsyncHandler[UserCreatedEvent],
                         to=AsyncEventHandlerProvider(CreateShopAndUpdateRegistrationWhileUserCreatedEventHandler))

        binder.multibind(AsyncHandler[WarehouseCreatedEvent],
                         to=AsyncEventHandlerProvider(UpdateShopWhileWarehouseCreatedEventHandler))

        # self.async_bind(binder, StoreCatalogCreatedEvent, StoreCatalogCreatedEventHandler)
        # self.async_bind(binder, StoreCatalogDeletedEvent, StoreCatalogDeletedEventHandler)
        #
        # # self.async_bind(binder, StoreCollectionCreatedEvent, StoreCollectionCreatedEventHandler)
        # self.async_bind(binder, StoreProductCreatedEvent, StoreProductCreatedOrUpdatedEventHandler)
        # self.async_bind(binder, StoreProductUpdatedEvent, StoreProductCreatedOrUpdatedEventHandler)
