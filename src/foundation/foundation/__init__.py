#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import injector
from sqlalchemy.engine import Connection

from foundation.events import AsyncHandler, Event, AsyncEventHandlerProvider


class FoundationHandlerFacade:
    def __init__(self, connection: Connection):
        self._conn = connection

    def record_event(self, event: Event):
        print(datetime.now(), event.__class__.__name__)


class FoundationModule(injector.Module):
    @injector.provider
    def facade(self, connection: Connection) -> FoundationHandlerFacade:
        return FoundationHandlerFacade(connection=connection)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[Event], to=AsyncEventHandlerProvider(RecordAllEventHandler))


class RecordAllEventHandler:
    @injector.inject
    def __init__(self, facade: FoundationHandlerFacade):
        self._facade = facade

    def __call__(self, event):
        self._facade.record_event(event)