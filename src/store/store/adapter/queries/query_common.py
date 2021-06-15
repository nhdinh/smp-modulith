#!/usr/bin/env python
# -*- coding: utf-8 -*-

import email_validator
from sqlalchemy import select, func, distinct
from sqlalchemy.engine import Connection

from store.adapter.store_db import store_table, store_owner_table, \
    store_collection_cache_table, store_catalog_table
from store.domain.entities.value_objects import StoreId, StoreCatalogId


def sql_fetch_store_by_owner(store_owner: str, conn: Connection, active_only: bool = True):
    try:
        email_validator.validate_email(store_owner)

        q = select([store_table.c.store_id]).where(store_table.c.owner_email == store_owner)
        if active_only:
            q = q.where(store_table.c.disabled == False)
        store_id = conn.scalar(q)

        # problem with the cache email from the `Store` table, we need to fetch the store by user_id
        if not store_id:
            q = select(store_table.c.store_id) \
                .join(store_owner_table, onclause=(store_table.c.owner == store_owner_table.c.id)) \
                .where(store_owner_table.c.email == store_owner)
            if active_only:
                q = q.where(store_table.c.disabled == False)
            store_id = conn.scalar(q)

        return store_id
    except Exception as exc:
        raise exc


def sql_fetch_catalog_by_reference(catalog_reference: str, store_id: StoreId, conn: Connection):
    q = select([store_catalog_table.c.catalog_id]) \
        .where(store_catalog_table.c.store_id == store_id) \
        .where(store_catalog_table.c.reference == catalog_reference)
    catalog_id = conn.scalar(q)

    return catalog_id


def sql_count_catalog_from_store(store_id: StoreId, conn: Connection, active_only: bool = False) -> int:
    catalog_count = conn.scalar(
        select([func.count(distinct(store_catalog_table.c.reference))]) \
            .select_from(store_catalog_table) \
            .where(store_catalog_table.c.store_id == store_id)
    )

    return catalog_count


def sql_count_collection_from_catalog(
        store_id: StoreId,
        catalog_id: StoreCatalogId,
        conn: Connection,
        active_only: bool = False
) -> int:
    collection_count = conn.scalar(
        select([func.count(distinct(store_collection_cache_table.c.collection_reference))]) \
            .select_from(store_collection_cache_table) \
            .where(store_collection_cache_table.c.store_id == store_id) \
            .where(store_collection_cache_table.c.catalog_id == catalog_id)
    )

    return collection_count


def sql_count_collection_from_store() -> int:
    pass
