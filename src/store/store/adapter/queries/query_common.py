#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

import email_validator
from sqlalchemy import select, func, distinct, and_
from sqlalchemy.engine import Connection

from store.adapter.shop_db import system_user_table, shop_table, shop_catalog_table, shop_collection_table, \
    shop_product_table, shop_product_collection_table, shop_users_table
from store.domain.entities.shop import Shop
from store.domain.entities.store_product import ShopProduct
from store.domain.entities.shop_supplier import ShopSupplier
from store.domain.entities.value_objects import ShopId, StoreCatalogId, StoreCollectionId


def sql_get_store_id_by_owner(store_owner: str, conn: Connection, active_only: bool = True) -> Optional[ShopId]:
    try:
        email_validator.validate_email(store_owner)

        q = select(shop_table.c.shop_id) \
            .join(shop_users_table, shop_table.c.shop_id == shop_users_table.c.shop_id) \
            .join(system_user_table, shop_users_table.c.user_id == system_user_table.c.user_id) \
            .where(system_user_table.c.email == store_owner)

        if active_only:
            q = q.where(shop_table.c.disabled == False)  # type:ignore
        store_id = conn.scalar(q)

        return store_id
    except Exception as exc:
        raise exc


def sql_get_collection_id_by_reference(collection_reference: str, catalog_reference: str, store_id: ShopId,
                                       conn: Connection) -> Optional[StoreCollectionId]:
    q = select(shop_collection_table.c.collection_id) \
        .join(shop_catalog_table, shop_collection_table.c.catalog_id == shop_catalog_table.c.catalog_id) \
        .where(and_(shop_collection_table.c.reference == collection_reference,
                    shop_catalog_table.c.reference == catalog_reference, shop_catalog_table.c.shop_id == store_id))

    return conn.scalar(q)


def sql_count_catalogs_in_store(store_id: ShopId, conn: Connection, active_only: bool = False) -> int:
    catalog_count = conn.scalar(
        select(func.count(distinct(shop_catalog_table.c.catalog_id))) \
            .where(shop_catalog_table.c.shop_id == store_id)
    )

    return catalog_count


def sql_count_collections_in_catalog(
        store_id: ShopId,
        catalog_id: StoreCatalogId,
        conn: Connection,
        active_only: bool = False
) -> int:
    q = select([func.count(distinct(shop_collection_table.c.collection_id))]).where(and_(
        shop_collection_table.c.catalog_id == catalog_id,
        shop_collection_table.c.shop_id == store_id
    ))

    return conn.scalar(q)


def sql_count_products_in_collection(
        store_id: ShopId,
        catalog_id: StoreCatalogId,
        collection_id: StoreCollectionId,
        conn: Connection,
        active_only: bool = False
) -> int:
    q = select([func.count(distinct(shop_product_table.c.product_id))]) \
        .join(shop_catalog_table, shop_product_table.c.catalog_id == shop_catalog_table.c.catalog_id) \
        .join(shop_product_collection_table,
              shop_product_table.c.product_id == shop_product_collection_table.c.product_id) \
        .where(and_(shop_product_collection_table.c.collection_id == collection_id,
                    shop_catalog_table.c.catalog_id == catalog_id,
                    shop_catalog_table.c.shop_id == store_id))

    return conn.scalar(q)


def sql_count_products_in_store(store_id: ShopId, conn: Connection) -> int:
    q = select([func.count(distinct(ShopProduct.product_id))]). \
        join(Shop).where(
        Shop.shop_id == store_id)
    return conn.scalar(q)


def sql_count_suppliers_in_store(store_id: ShopId, conn: Connection) -> int:
    q = select([func.count(distinct(ShopSupplier.supplier_id))]).join(Shop).where(Shop.shop_id == store_id)
    return conn.scalar(q)
