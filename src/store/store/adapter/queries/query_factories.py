#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import select
from sqlalchemy.sql import Select

from store.adapter.store_db import shop_product_table, store_brand_table, store_catalog_table, shop_collection_table, \
    shop_product_collection_table, store_supplier_table, store_product_supplier_table, shop_user_table, shop_table, \
    store_product_data_cache_table, shop_managers_table
from store.domain.entities.shop_user import ShopUserId
from store.domain.entities.value_objects import ShopId, StoreProductId


def store_catalog_query_factory(store_id: ShopId) -> Select:
    return select([
        store_catalog_table.c.catalog_id,
        store_catalog_table.c.title.label('catalog_title'),
        store_catalog_table.c.default.label('is_default_catalog'),
        store_catalog_table.c.image.label('catalog_image'),
        store_catalog_table.c.disabled.label('is_catalog_disabled'),
    ]).where(store_catalog_table.c.shop_id == store_id)


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

        store_catalog_table.c.catalog_id,
        store_catalog_table.c.title.label('catalog_title'),
        store_catalog_table.c.default.label('is_default_catalog'),
        store_catalog_table.c.image.label('catalog_image'),
        store_catalog_table.c.disabled.label('is_catalog_disabled'),

        store_brand_table.c.brand_id,
        store_brand_table.c.name.label('brand_name'),
        store_brand_table.c.logo,
    ]) \
        .join(store_catalog_table, shop_product_table.c.catalog_id == store_catalog_table.c.catalog_id) \
        .join(store_brand_table, shop_product_table.c.brand_id == store_brand_table.c.brand_id, isouter=True) \
        .where(shop_product_table.c.shop_id == store_id)

    query = select([
        shop_product_table,
        store_product_data_cache_table
    ]) \
        .join(store_product_data_cache_table,
              shop_product_table.c.product_id == store_product_data_cache_table.c.product_cache_id) \
        .where(store_product_data_cache_table.c.shop_id == store_id)

    return query


def get_product_query_factory(product_id: StoreProductId) -> Select:
    query = select([
        shop_product_table,

        store_catalog_table.c.catalog_id,
        store_catalog_table.c.title.label('catalog_title'),
        store_catalog_table.c.default.label('is_default_catalog'),
        store_catalog_table.c.image.label('catalog_image'),
        store_catalog_table.c.disabled.label('is_catalog_disabled'),

        store_brand_table.c.brand_id,
        store_brand_table.c.name.label('brand_name'),
        store_brand_table.c.logo,
    ]) \
        .join(store_catalog_table, shop_product_table.c.catalog_id == store_catalog_table.c.catalog_id) \
        .join(store_brand_table, shop_product_table.c.brand_id == store_brand_table.c.brand_id, isouter=True) \
        .where(shop_product_table.c.product_id == product_id)

    return query


def list_product_collections_query_factory(product_id: StoreProductId):
    query = store_collection_query_factory() \
        .join(shop_product_collection_table,
              shop_product_table.c.product_id == shop_product_collection_table.c.product_id) \
        .join(shop_collection_table,
              shop_collection_table.c.collection_id == shop_product_collection_table.c.collection_id) \
        .where(shop_product_table.c.product_id == product_id)

    return query


def get_store_query_factory(store_owner_email: str):
    query = select(shop_table) \
        .join(shop_managers_table, shop_table.c.shop_id == shop_managers_table.c.shop_id) \
        .join(shop_user_table, shop_managers_table.c.user_id == shop_user_table.c.user_id) \
        .where(shop_user_table.c.email == store_owner_email)
    return query


def get_suppliers_bound_to_product_query(product_id: StoreProductId):
    query = select(store_supplier_table) \
        .join(store_product_supplier_table,
              store_product_supplier_table.c.supplier_id == store_supplier_table.c.supplier_id) \
        .where(store_product_supplier_table.c.product_id == product_id)
    return query
