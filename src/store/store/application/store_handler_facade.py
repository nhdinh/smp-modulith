#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection

from store.domain.entities.value_objects import StoreOwnerId, StoreId


class StoreHandlerFacade:
    def __init__(self, connection: Connection):
        self._conn = connection

    def create_store(
            self,
            store_id: StoreId,
            store_owner: StoreOwnerId,
            store_name: str
    ) -> None:
        pass


class StoreRegistrationConfirmedEventHandler:
    @injector.inject
    def __init__(self, facade: StoreHandlerFacade):
        self._facade = facade

    def __call__(self, event):
        self._facade.create_store(
            store_id=event.store_id,
            store_name=event.store_name,
            store_owner=event.store_id
        )
