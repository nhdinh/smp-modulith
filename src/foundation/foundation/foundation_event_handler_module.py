#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection

from foundation.application.foundation_event_handlers_facade import RecordAllEventHandler, FoundationHandlerFacade
from foundation.events import AsyncEventHandlerProvider, AsyncHandler, Event


class FoundationEventHandlerModule(injector.Module):
    @injector.provider
    def facade(self, connection: Connection) -> FoundationHandlerFacade:
        return FoundationHandlerFacade(connection=connection)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[Event], to=AsyncEventHandlerProvider(RecordAllEventHandler))
