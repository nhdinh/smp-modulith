#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import select
from sqlalchemy.sql import Select

from store.adapter.shop_db import shop_product_table, shop_brand_table, shop_catalog_table, shop_collection_table, \
    shop_product_collection_table, shop_supplier_table, shop_product_supplier_table, shop_user_table, shop_table, \
    shop_product_data_cache_table, shop_users_table
from store.domain.entities.shop_user import ShopUserId
from store.domain.entities.value_objects import ShopId, ShopProductId


def store_catalog_query_factory(store_id: ShopId) -> Select:
    return select([
        shop_catalog_table.c.catalog_id,
        shop_catalog_table.c.title.label('catalog_title'),
        shop_catalog_table.c.default.label('is_default_catalog'),
        shop_catalog_table.c.image.label('catalog_image'),
        shop_catalog_table.c.disabled.label('is_catalog_disabled'),
    ]).where(shop_catalog_table.c.shop_id == store_id)


def store_collection_query_factory() -> Select:
    query = select([
        shop_collection_table.c.collection_id,
        shop_collection_table.c.title,
        shop_collection_table.c.disabled.label('is_collection_disabled')
    ])

    return query


def list_store_product_query_factory(store_id: ShopId) -> Select:
    query = select([
        shop_product_table,

        shop_catalog_table.c.catalog_id,
        shop_catalog_table.c.title.label('catalog_title'),
        shop_catalog_table.c.default.label('is_default_catalog'),
        shop_catalog_table.c.image.label('catalog_image'),
        shop_catalog_table.c.disabled.label('is_catalog_disabled'),

        shop_brand_table.c.brand_id,
        shop_brand_table.c.name.label('brand_name'),
        shop_brand_table.c.logo,
    ]) \
        .join(shop_catalog_table, shop_product_table.c.catalog_id == shop_catalog_table.c.catalog_id) \
        .join(shop_brand_table, shop_product_table.c.brand_id == shop_brand_table.c.brand_id, isouter=True) \
        .where(shop_product_table.c.shop_id == store_id)

    query = select([
        shop_product_table,
        shop_product_data_cache_table
    ]) \
        .join(shop_product_data_cache_table,
              shop_product_table.c.product_id == shop_product_data_cache_table.c.product_cache_id) \
        .where(shop_product_data_cache_table.c.shop_id == store_id)

    return query


def get_product_query_factory(product_id: ShopProductId) -> Select:
    query = select([
        shop_product_table,

        shop_catalog_table.c.catalog_id,
        shop_catalog_table.c.title.label('catalog_title'),
        shop_catalog_table.c.default.label('is_default_catalog'),
        shop_catalog_table.c.image.label('catalog_image'),
        shop_catalog_table.c.disabled.label('is_catalog_disabled'),

        shop_brand_table.c.brand_id,
        shop_brand_table.c.name.label('brand_name'),
        shop_brand_table.c.logo,
    ]) \
        .join(shop_catalog_table, shop_product_table.c.catalog_id == shop_catalog_table.c.catalog_id) \
        .join(shop_brand_table, shop_product_table.c.brand_id == shop_brand_table.c.brand_id, isouter=True) \
        .where(shop_product_table.c.product_id == product_id)

    return query


def list_product_collections_query_factory(product_id: ShopProductId):
    query = store_collection_query_factory() \
        .join(shop_product_collection_table,
              shop_product_table.c.product_id == shop_product_collection_table.c.product_id) \
        .join(shop_collection_table,
              shop_collection_table.c.collection_id == shop_product_collection_table.c.collection_id) \
        .where(shop_product_table.c.product_id == product_id)

    return query


def get_store_query_factory(store_owner_email: str):
    query = select(shop_table) \
        .join(shop_users_table, shop_table.c.shop_id == shop_users_table.c.shop_id) \
        .join(shop_user_table, shop_users_table.c.user_id == shop_user_table.c.user_id) \
        .where(shop_user_table.c.email == store_owner_email)
    return query


def get_suppliers_bound_to_product_query(product_id: ShopProductId):
    query = select(shop_supplier_table) \
        .join(shop_product_supplier_table,
              shop_product_supplier_table.c.supplier_id == shop_supplier_table.c.supplier_id) \
        .where(shop_product_supplier_table.c.product_id == product_id)
    return query
