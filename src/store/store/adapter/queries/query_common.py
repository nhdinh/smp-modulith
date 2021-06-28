#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

import email_validator
from sqlalchemy import select, func, distinct, and_
from sqlalchemy.engine import Connection

from store.domain.entities.store import Store
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_product import StoreProduct
from store.domain.entities.value_objects import StoreId, StoreCatalogId, StoreCatalogReference, \
    StoreCollectionReference, StoreCollectionId


def sql_get_store_id_by_owner(store_owner: str, conn: Connection, active_only: bool = True) -> Optional[StoreId]:
    try:
        email_validator.validate_email(store_owner)

        q = select([Store.store_id]).where(Store.owner_email == store_owner)
        if active_only:
            q = q.where(Store.disabled == False)
        store_id = conn.scalar(q)

        # problem with the cache email from the `Store` table, we need to fetch the store by user_id
        if not store_id:
            q = select(Store.store_id) \
                .join(StoreOwner) \
                .where(StoreOwner.email == store_owner)
            if active_only:
                q = q.where(Store.disabled == False)
            store_id = conn.scalar(q)

        return store_id
    except Exception as exc:
        raise exc


def sql_get_catalog_id_by_reference(catalog_reference: str, store_id: StoreId, conn: Connection) -> Optional[
    StoreCatalogId]:
    q = select([StoreCatalog]).join(Store) \
        .where(and_(StoreCatalog.reference == catalog_reference, Store.store_id == store_id))
    catalog_id = conn.scalar(q)

    return catalog_id


def sql_get_collection_id_by_reference(collection_reference: str, catalog_reference: str, store_id: StoreId,
                                       conn: Connection) -> Optional[StoreCollectionId]:
    q = select([StoreCollection.collection_id]).join(StoreCatalog).join(Store) \
        .where(StoreCollection.reference == collection_reference) \
        .where(Store.store_id == store_id)
    collection_id = conn.scalar(q)

    return collection_id


def sql_count_catalogs_in_store(store_id: StoreId, conn: Connection, active_only: bool = False) -> int:
    catalog_count = conn.scalar(
        select([func.count(distinct(StoreCatalog.catalog_id))]).join(Store) \
            .where(Store.store_id == store_id)
    )

    return catalog_count


def sql_count_collections_in_catalog(
        store_id: StoreId,
        catalog_id: StoreCatalogId,
        conn: Connection,
        active_only: bool = False
) -> int:
    collection_count = conn.scalar(
        select([func.count(distinct(StoreCollection.collection_id))]).join(StoreCatalog).join(Store) \
            .where(Store.store_id == store_id) \
            .where(StoreCatalog.catalog_id == catalog_id)
    )

    return collection_count


def sql_count_products_in_collection(
        store_id: StoreId,
        catalog_reference: StoreCatalogReference,
        collection_reference: StoreCollectionReference,
        conn: Connection,
        active_only: bool = False
) -> int:
    # products_count = conn.scalar(
    #     select([func.count(distinct(store_product_table.c.product_id))]) \
    #         .select_from(store_product_table) \
    #         .join(store_collection_table,
    #               onclause=(store_collection_table.c.collection_id == store_product_table.c.collection_id)) \
    #         .join(store_catalog_table,
    #               onclause=(store_catalog_table.c.catalog_id == store_collection_table.c.catalog_id)) \
    #         .where(store_catalog_table.c.store_id == store_id)
    # )

    q = select([func.count(distinct(StoreProduct.product_id))]) \
        .join(StoreCollection, StoreProduct.collection_id == StoreCollection.collection_id, isouter=True) \
        .join(StoreCatalog, StoreCollection.catalog_id == StoreCatalog.catalog_id, isouter=True) \
        .join(Store, Store.store_id == StoreCatalog.store_id, isouter=True) \
        .where(and_(StoreCollection.reference == collection_reference,
                    StoreCatalog.reference == catalog_reference,
                    Store.store_id == store_id
                    ))

    products_count = conn.scalar(q)

    return products_count


def sql_count_products_in_store(store_id: StoreId, conn: Connection) -> int:
    q = select([func.count(distinct(StoreProduct.product_id))]). \
        join(Store).where(
        Store.store_id == store_id)
    return conn.scalar(q)
