#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection

from foundation.events import (
    EventHandlerProvider,
    Handler, EventBus,
)
from identity.domain.events import UnexistentUserRequestEvent
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.shop_handler_facade import (
    ShopHandlerFacade, DisableUnexistentSystemUserHandler,
)


class ShopEventHandlerModule(injector.Module):
    @injector.provider
    def facade(self, uow: ShopUnitOfWork, conn: Connection, eventbus: EventBus) -> ShopHandlerFacade:
        return ShopHandlerFacade(uow, conn, eventbus)

    def configure(self, binder: injector.Binder) -> None:
        self._configure_handler_bindings(binder=binder)
        self._configure_async_handler_bindings(binder=binder)

    def _configure_handler_bindings(self, binder: injector.Binder) -> None:
        # Mark an user as deleted when receive an UnexistentUserRequestEvent from Identity services
        binder.multibind(
            Handler[UnexistentUserRequestEvent],
            to=EventHandlerProvider(DisableUnexistentSystemUserHandler)
        )

    def _configure_async_handler_bindings(self, binder: injector.Binder) -> None:
        ...
