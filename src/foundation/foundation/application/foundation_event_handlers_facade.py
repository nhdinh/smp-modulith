#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import injector
from foundation.events import Event, WillRaiseExceptionEvent
from sqlalchemy.engine import Connection


class FoundationHandlerFacade:
    def __init__(self, connection: Connection):
        self._conn = connection

    def save_event_data(self, event: Event):
        if isinstance(event, WillRaiseExceptionEvent):
            raise Exception('Exception of WillRaiseExceptionEvent')


class RecordAllEventHandler:
    @injector.inject
    def __init__(self, facade: FoundationHandlerFacade):
        self._facade = facade

    def __call__(self, event):
        self._facade.save_event_data(event)
