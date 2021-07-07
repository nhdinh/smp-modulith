#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Union

import injector
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection

from foundation.logger import logger
from store.adapter.queries.query_factories import get_product_query_factory, get_product_collections_query_factory
from store.adapter.store_db import store_catalog_table, \
    store_collection_table, store_product_data_cache_table
from store.application.queries.dtos.store_catalog_dto import _row_to_catalog_dto
from store.application.queries.dtos.store_collection_dto import _row_to_collection_dto
from store.application.queries.dtos.store_product_brand_dto import _row_to_brand_dto
from store.application.queries.dtos.store_supplier_dto import _row_to_supplier_dto
from store.domain.entities.store_product import StoreProductId
from store.domain.entities.value_objects import StoreCatalogId
from store.domain.events.store_catalog_events import StoreCatalogDeletedEvent
from store.domain.events.store_product_events import StoreProductCreatedEvent, StoreProductUpdatedEvent


class StoreHandlerFacade:
    def __init__(self, connection: Connection):
        self._conn = connection

    def do_something(self):
        pass

    # def update_store_catalog_cache(self, store_id: StoreId, catalog_id: StoreCatalogId, catalog_reference: str):
    #     query = insert(store_catalog_cache_table).values(**{
    #         'store_id': store_id,
    #         'catalog_id': catalog_id,
    #         'catalog_reference': catalog_reference
    #     })
    #
    #     self._conn.execute(query)
    #
    # def update_store_collection_cache(self, store_id: StoreId, catalog_id: StoreCatalogId,
    #                                   collection_id: StoreCollectionId, collection_reference: str):
    #     query = insert(store_collection_cache_table).values(**{
    #         'store_id': store_id,
    #         'catalog_id': catalog_id,
    #         'collection_id': collection_id,
    #         'collection_reference': collection_reference
    #     })
    #
    #     self._conn.execute(query)

    def update_store_cache(self, store_id):
        # just to do something with the cache
        pass

    def delete_orphan_catalog_children(self, catalog_id: StoreCatalogId):
        query = delete(store_catalog_table).where(store_catalog_table.c.catalog_id == catalog_id)
        self._conn.execute(query)

        query = delete(store_collection_table).where(store_collection_table.c.catalog_id is None)
        self._conn.execute(query)

    def update_store_product_cache(self, product_id: StoreProductId, is_updated=False, updated_keys=[]):
        """
        Update the product info into cache

        :param product_id: id of the updated product
        """
        try:
            query = get_product_query_factory(product_id=product_id)
            product_data = self._conn.execute(query).first()

            if not product_data:
                return

            # get catalog and brand
            catalog_json = _row_to_catalog_dto(product_data, collections=[])
            brand_json = _row_to_brand_dto(product_data)

            # get collections
            query = get_product_collections_query_factory(product_id=product_id)
            collections_data = self._conn.execute(query).all()
            collections_json = [_row_to_collection_dto(r) for r in collections_data]

            # get suppliers
            query = get_suppliers_bound_to_product_query(product_id=product_id)
            suppliers_data = self._conn.execute(query).all()
            suppliers_data = [_row_to_supplier_dto(r) for r in suppliers_data]

            # insert data
            data = {
                'product_cache_id': product_id,
                'catalog_json': catalog_json,
                'collections_json': collections_json,
                'brand_json': brand_json
            }
            stmt = insert(store_product_data_cache_table).values(**data)

            # or update if duplicated
            on_duplicate_key_stmt = stmt.on_conflict_do_update(
                constraint=store_product_data_cache_table.primary_key,
                set_=data
            )

            self._conn.execute(on_duplicate_key_stmt)
        except Exception as exc:
            logger.exception(exc)


# class StoreCatalogCreatedEventHandler:
#     @injector.inject
#     def __init__(self, facade: StoreHandlerFacade):
#         self._facade = facade
#
#     def __call__(self, event: StoreCatalogCreatedEvent) -> None:
#         self._facade.update_store_catalog_cache(event.store_id, event.catalog_id, event.catalog_reference)


class StoreCatalogDeletedEventHandler:
    @injector.inject
    def __init__(self, facade: StoreHandlerFacade):
        self._facade = facade

    def __call__(self, event: StoreCatalogDeletedEvent) -> None:
        self._facade.delete_orphan_catalog_children(event.catalog_id)
        # self._facade.update_store_catalog_cache(event.store_id)


# class StoreCollectionCreatedEventHandler:
#     @injector.inject
#     def __init__(self, facade: StoreHandlerFacade):
#         self._facade = facade
#
#     def __call__(self, event: StoreCollectionCreatedEvent) -> None:
#         self._facade.update_store_collection_cache(
#             event.store_id,
#             event.catalog_id,
#             event.collection_id,
#             event.collection_reference
#         )

class StoreProductCreatedOrUpdatedEventHandler:
    @injector.inject
    def __init__(self, facade: StoreHandlerFacade):
        self._facade = facade

    def __call__(self, event: Union[StoreProductCreatedEvent, StoreProductUpdatedEvent]) -> None:
        if isinstance(event, StoreProductCreatedEvent):
            self._facade.update_store_product_cache(event.product_id)
        elif isinstance(event, StoreProductUpdatedEvent):
            self._facade.update_store_product_cache(event.product_id, is_updated=True, updated_keys=event.updated_keys)
