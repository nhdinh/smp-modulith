#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from foundation.events import AsyncHandler, EveryModuleMustCatchThisEvent, AsyncEventHandlerProvider

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.shop_handler_facade import ShopHandlerFacade, Shop_CatchAllEventHandler


class ShopEventHandlerModule(injector.Module):
    @injector.provider
    def facade(self, uow: ShopUnitOfWork) -> ShopHandlerFacade:
        return ShopHandlerFacade(uow)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[EveryModuleMustCatchThisEvent],
                         to=AsyncEventHandlerProvider(Shop_CatchAllEventHandler))
