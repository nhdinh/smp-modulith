#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection

from foundation import AsyncEventHandlerProvider, AsyncHandler
from foundation.events import EveryModuleMustCatchThisEvent, EventBus
from identity.identity_handler_facade import (
    Identity_CatchAllEventHandler,
    IdentityHandlerFacade,
)


class IdentityEventHandlerModule(injector.Module):
    @injector.provider
    def facade(self, conn: Connection, event_bus: EventBus) -> IdentityHandlerFacade:
        return IdentityHandlerFacade(conn, event_bus)

    def configure(self, binder: injector.Binder) -> None:
        # AsyncHandler binding
        binder.multibind(AsyncHandler[EveryModuleMustCatchThisEvent],
                         to=AsyncEventHandlerProvider(Identity_CatchAllEventHandler))
