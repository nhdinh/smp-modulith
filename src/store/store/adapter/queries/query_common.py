#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from sqlalchemy import select, func, distinct, and_
from sqlalchemy.engine import Connection

from store.adapter.shop_db import shop_table, shop_catalog_table, shop_collection_table, \
    shop_product_table, shop_product_collection_table, shop_users_table
from store.domain.entities.shop import Shop
from store.domain.entities.shop_supplier import ShopSupplier
from store.domain.entities.shop_user import SystemUserId
from store.domain.entities.store_product import ShopProduct
from store.domain.entities.value_objects import ShopId, ShopCatalogId, StoreCollectionId, ShopStatus


def sql_get_store_id_by_owner(store_owner: str, conn: Connection, active_only: bool = True) -> Optional[ShopId]:
    raise NotImplementedError


def sql_verify_shop_id_with_partner_id(shop_id: ShopId, partner_id: SystemUserId, conn: Connection,
                                       active_only: bool = True) -> bool:
    try:
        q = select(shop_table.c.shop_id) \
            .join(shop_users_table, shop_users_table.c.shop_id == shop_table.c.shop_id) \
            .where(shop_users_table.c.user_id == partner_id)

        if active_only:
            q = q.where(shop_table.c.status == ShopStatus.NORMAL)

        shop_id = conn.scalar(q)

        if shop_id:
            return True
        else:
            return False
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
