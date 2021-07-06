#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

import email_validator
from sqlalchemy import select, func, distinct, and_
from sqlalchemy.engine import Connection

from store.adapter.store_db import store_owner_table, store_table, store_catalog_table, store_collection_table, \
    store_product_table, store_product_collection_table
from store.domain.entities.store import Store
from store.domain.entities.value_objects import StoreId, StoreCatalogId, StoreCollectionId
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.store_product import StoreProduct
from store.domain.entities.store_supplier import StoreSupplier


def sql_get_store_id_by_owner(store_owner: str, conn: Connection, active_only: bool = True) -> Optional[StoreId]:
    try:
        email_validator.validate_email(store_owner)

        q = select([store_table.c.store_id]).where(store_table.c.owner_email == store_owner)  # type:ignore
        if active_only:
            q = q.where(store_table.c.disabled == False)  # type:ignore
        store_id = conn.scalar(q)

        # problem with the cache email from the `Store` table, we need to fetch the store by user_id
        if not store_id:
            q = select(store_table.c.store_id) \
                .join(store_owner_table, store_table.c._owner_id == store_owner_table.c.id) \
                .where(store_owner_table.c.email == store_owner)

            if active_only:
                q = q.where(store_table.c.disabled == False)  # type:ignore
            store_id = conn.scalar(q)

        return store_id
    except Exception as exc:
        raise exc


def sql_get_collection_id_by_reference(collection_reference: str, catalog_reference: str, store_id: StoreId,
                                       conn: Connection) -> Optional[StoreCollectionId]:
    q = select(store_collection_table.c.collection_id) \
        .join(store_catalog_table, store_collection_table.c.catalog_id == store_catalog_table.c.catalog_id) \
        .where(and_(store_collection_table.c.reference == collection_reference,
                    store_catalog_table.c.reference == catalog_reference, store_catalog_table.c.store_id == store_id))

    return conn.scalar(q)


def sql_count_catalogs_in_store(store_id: StoreId, conn: Connection, active_only: bool = False) -> int:
    catalog_count = conn.scalar(
        select(func.count(distinct(store_catalog_table.c.catalog_id))) \
            .where(store_catalog_table.c.store_id == store_id)
    )

    return catalog_count


def sql_count_collections_in_catalog(
        store_id: StoreId,
        catalog_id: StoreCatalogId,
        conn: Connection,
        active_only: bool = False
) -> int:
    q = select([func.count(distinct(store_collection_table.c.collection_id))]).where(and_(
        store_collection_table.c.catalog_id == catalog_id,
        store_collection_table.c.store_id == store_id
    ))

    return conn.scalar(q)


def sql_count_products_in_collection(
        store_id: StoreId,
        catalog_id: StoreCatalogId,
        collection_id: StoreCollectionId,
        conn: Connection,
        active_only: bool = False
) -> int:
    q = select([func.count(distinct(store_product_table.c.product_id))]) \
        .join(store_catalog_table, store_product_table.c.catalog_id == store_catalog_table.c.catalog_id) \
        .join(store_product_collection_table,
              store_product_table.c.product_id == store_product_collection_table.c.product_id) \
        .where(and_(store_product_collection_table.c.collection_id == collection_id,
                    store_catalog_table.c.catalog_id == catalog_id,
                    store_catalog_table.c.store_id == store_id))

    return conn.scalar(q)


def sql_count_products_in_store(store_id: StoreId, conn: Connection) -> int:
    q = select([func.count(distinct(StoreProduct.product_id))]). \
        join(Store).where(
        Store.store_id == store_id)
    return conn.scalar(q)


def sql_count_suppliers_in_store(store_id: StoreId, conn: Connection) -> int:
    q = select([func.count(distinct(StoreSupplier.supplier_id))]).join(Store).where(Store.store_id == store_id)
    return conn.scalar(q)
