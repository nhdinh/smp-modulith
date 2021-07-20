#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from sqlalchemy import and_, distinct, func, select
from sqlalchemy.engine import Connection

from shop.adapter.shop_db import (
    shop_catalog_table,
    shop_collection_table,
    shop_product_collection_table,
    shop_product_supplier_table,
    shop_product_table,
    shop_supplier_table,
    shop_table,
    shop_users_table,
)
from shop.domain.entities.shop import Shop
from shop.domain.entities.shop_product import ShopProduct
from shop.domain.entities.value_objects import (
    ShopCatalogId,
    ShopCollectionId,
    ShopId,
    ShopStatus,
    ShopSupplierId,
    SystemUserId,
)


def sql_verify_shop_id(shop_id: ShopId, partner_id: SystemUserId, conn: Connection,
                       active_only: bool = True) -> bool:
    try:
        q = select(shop_table.c.shop_id) \
            .join(shop_users_table, shop_users_table.c.shop_id == shop_table.c.shop_id) \
            .where(and_(shop_users_table.c.user_id == partner_id, shop_table.c.shop_id == shop_id))

        if active_only:
            q = q.where(shop_table.c.status != ShopStatus.DISABLED)

        shop_id_from_db = conn.scalar(q)

        if shop_id_from_db:
            return True
        else:
            return False
    except Exception as exc:
        raise exc


def sql_get_collection_id_by_reference(collection_id: ShopCollectionId, shop_id: ShopId,
                                       conn: Connection) -> Optional[ShopCollectionId]:
    q = select(shop_collection_table.c.collection_id) \
        .join(shop_catalog_table, shop_collection_table.c.catalog_id == shop_catalog_table.c.catalog_id) \
        .where(and_(shop_collection_table.c.reference == collection_id, shop_catalog_table.c.shop_id == shop_id))

    return conn.scalar(q)


def sql_count_catalogs_in_shop(store_id: ShopId, conn: Connection, active_only: bool = False) -> int:
    catalog_count = conn.scalar(
        select(func.count(distinct(shop_catalog_table.c.catalog_id))) \
            .where(shop_catalog_table.c.shop_id == store_id)
    )

    return catalog_count


def sql_count_collections_in_catalog(
        store_id: ShopId,
        catalog_id: ShopCatalogId,
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
        catalog_id: ShopCatalogId,
        collection_id: ShopCollectionId,
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
    q = select([func.count(distinct(shop_product_table.c.product_id))]) \
        .where(shop_product_table.c.shop_id == store_id)
    return conn.scalar(q)


def sql_count_all_suppliers(shop_id: ShopId, conn: Connection) -> int:
    q = select([func.count(distinct(shop_supplier_table.c.supplier_id))]).where(
        shop_supplier_table.c.shop_id == shop_id)
    return conn.scalar(q)


def sql_count_all_products_by_supplier(shop_id: ShopId, supplier_id: ShopSupplierId, conn: Connection) -> int:
    q = select([func.count(distinct(shop_product_table.c.product_id))]) \
        .join(shop_product_supplier_table,
              shop_product_table.c.product_id == shop_product_supplier_table.c.product_id) \
        .where(and_(shop_product_table.c.shop_id == shop_id, shop_product_supplier_table.c.supplier_id == supplier_id))
    return conn.scalar(q)
