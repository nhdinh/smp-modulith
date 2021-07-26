#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, Callable

from sqlalchemy import and_, distinct, func, select
from sqlalchemy.engine import Connection

from shop.adapter.shop_db import (
    shop_catalog_table,
    shop_collection_table,
    shop_product_collection_table,
    shop_product_table,
    shop_table,
    shop_users_table,
)
from shop.domain.entities.value_objects import (
    ShopCatalogId,
    ShopCollectionId,
    ShopId,
    ShopStatus,
    SystemUserId,
)
from web_app.serialization.dto import list_response_factory


def sql_get_authorized_shop_id(shop_id: ShopId, current_user_id: SystemUserId, conn: Connection,
                               active_only: bool = True) -> bool:
    try:
        q = select(shop_table.c.shop_id) \
            .join(shop_users_table, shop_users_table.c.shop_id == shop_table.c.shop_id) \
            .where(and_(shop_users_table.c.user_id == current_user_id, shop_table.c.shop_id == shop_id))

        if active_only:
            q = q.where(shop_table.c.status == ShopStatus.NORMAL)

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


def sql_count_or_empty_return(counting_query: Callable, conn: Connection, **kwargs) -> int:
    try:
        if callable(counting_query):
            counting_query = counting_query(**kwargs)

        return conn.scalar(counting_query) or 0
    except Exception as exc:
        raise exc
