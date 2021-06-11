#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy import insert
from sqlalchemy.engine import Connection

from store.adapter.store_db import store_catalog_cache_table, store_collection_cache_table
from store.domain.entities.value_objects import StoreCatalogId, StoreId, StoreCollectionId
from store.domain.events.store_catalog_events import StoreCatalogCreatedEvent, StoreCollectionCreatedEvent


class StoreHandlerFacade:
    def __init__(self, connection: Connection):
        self._conn = connection

    def do_something(self):
        pass

    def update_store_catalog_cache(self, store_id: StoreId, catalog_id: StoreCatalogId, catalog_reference: str):
        query = insert(store_catalog_cache_table).values(**{
            'store_id': store_id,
            'catalog_id': catalog_id,
            'catalog_reference': catalog_reference
        })

        self._conn.execute(query)

    def update_store_collection_cache(self, store_id: StoreId, catalog_id: StoreCatalogId,
                                      collection_id: StoreCollectionId, collection_reference: str):
        query = insert(store_collection_cache_table).value(**{
            'store_id': store_id,
            'catalog_id': catalog_id,
            'collection_id': collection_id,
            'collection_reference': collection_reference
        })

        self._conn.execute(query)

    def update_store_cache(self, store_id):
        # just to do something with the cache
        pass


# class StoreCreatedEventHandler:
#     @injector.inject
#     def __init__(self, facace: StoreHandlerFacade):
#         self._facade = facace
#
#     def __call__(self, event: StoreCreatedEvent) -> None:
#         self._facade.update_store_cache(event.store_id)


class StoreCatalogCreatedEventHandler:
    @injector.inject
    def __init__(self, facade: StoreHandlerFacade):
        self._facade = facade

    def __call__(self, event: StoreCatalogCreatedEvent) -> None:
        self._facade.update_store_catalog_cache(event.store_id, event.catalog_id, event.catalog_reference)


class StoreCollectionCreatedEventHandler:
    @injector.inject
    def __init__(self, facade: StoreHandlerFacade):
        self._facade = facade

    def __call__(self, event: StoreCollectionCreatedEvent) -> None:
        self._facade.update_store_collection_cache(
            event.store_id,
            event.catalog_id,
            event.collection_id,
            event.collection_reference
        )
