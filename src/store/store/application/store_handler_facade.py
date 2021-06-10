#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy import insert
from sqlalchemy.engine import Connection

from store.adapter.store_db import store_catalog_cache_table
from store.domain.entities.value_objects import StoreCatalogId, StoreId
from store.domain.events.store_catalog_events import StoreCatalogCreatedEvent


class StoreHandlerFacade:
    def __init__(self, connection: Connection):
        self._conn = connection

    def do_something(self):
        pass

    def update_store_cache(self, store_id: StoreId, catalog_id: StoreCatalogId, catalog_reference: str):
        query = insert(store_catalog_cache_table).values(**{
            'store_id': store_id,
            'catalog_id': catalog_id,
            'catalog_reference': catalog_reference
        })

        self._conn.execute(query)




class StoreCatalogCreatedEventHandler:
    @injector.inject
    def __init__(self, facade: StoreHandlerFacade):
        self._facade = facade

    def __call__(self, event: StoreCatalogCreatedEvent) -> None:
        self._facade.update_store_cache(event.store_id, event.catalog_id, event.catalog_reference)
