#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import select
from sqlalchemy.sql import Select

from store.adapter.store_db import store_product_table, store_brand_table, store_catalog_table, store_collection_table, \
    store_product_collection_table, store_supplier_table, store_product_supplier_table, store_owner_table, store_table, \
    store_product_data_cache_table
from store.domain.entities.store_owner import StoreOwnerId
from store.domain.entities.value_objects import StoreId, StoreProductId


def store_catalog_query_factory(store_id: StoreId) -> Select:
    return select([
        store_catalog_table.c.catalog_id,
        store_catalog_table.c.title.label('catalog_title'),
        store_catalog_table.c.default.label('is_default_catalog'),
        store_catalog_table.c.image.label('catalog_image'),
        store_catalog_table.c.disabled.label('is_catalog_disabled'),
    ]).where(store_catalog_table.c.store_id == store_id)


def store_collection_query_factory() -> Select:
    query = select([
        store_collection_table.c.collection_id,
        store_collection_table.c.title,
        store_collection_table.c.disabled.label('is_collection_disabled')
    ])

    return query


def list_store_product_query_factory(store_id: StoreId) -> Select:
    query = select([
        store_product_table,

        store_catalog_table.c.catalog_id,
        store_catalog_table.c.title.label('catalog_title'),
        store_catalog_table.c.default.label('is_default_catalog'),
        store_catalog_table.c.image.label('catalog_image'),
        store_catalog_table.c.disabled.label('is_catalog_disabled'),

        store_brand_table.c.brand_id,
        store_brand_table.c.name.label('brand_name'),
        store_brand_table.c.logo,
    ]) \
        .join(store_catalog_table, store_product_table.c.catalog_id == store_catalog_table.c.catalog_id) \
        .join(store_brand_table, store_product_table.c.brand_id == store_brand_table.c.brand_id, isouter=True) \
        .where(store_product_table.c.store_id == store_id)

    query = select([
        store_product_table,
        store_product_data_cache_table
    ]) \
        .join(store_product_data_cache_table,
              store_product_table.c.product_id == store_product_data_cache_table.c.product_cache_id) \
        .where(store_product_data_cache_table.c.store_id == store_id)

    return query


def get_product_query_factory(product_id: StoreProductId) -> Select:
    query = select([
        store_product_table,

        store_catalog_table.c.catalog_id,
        store_catalog_table.c.title.label('catalog_title'),
        store_catalog_table.c.default.label('is_default_catalog'),
        store_catalog_table.c.image.label('catalog_image'),
        store_catalog_table.c.disabled.label('is_catalog_disabled'),

        store_brand_table.c.brand_id,
        store_brand_table.c.name.label('brand_name'),
        store_brand_table.c.logo,
    ]) \
        .join(store_catalog_table, store_product_table.c.catalog_id == store_catalog_table.c.catalog_id) \
        .join(store_brand_table, store_product_table.c.brand_id == store_brand_table.c.brand_id, isouter=True) \
        .where(store_product_table.c.product_id == product_id)

    return query


def list_product_collections_query_factory(product_id: StoreProductId):
    query = store_collection_query_factory() \
        .join(store_product_collection_table,
              store_product_table.c.product_id == store_product_collection_table.c.product_id) \
        .join(store_collection_table,
              store_collection_table.c.collection_id == store_product_collection_table.c.collection_id) \
        .where(store_product_table.c.product_id == product_id)

    return query


def get_store_query_factory(store_owner_email: str):
    query = select(store_table) \
        .join(store_owner_table, store_table.c._owner_id == store_owner_table.c.user_id) \
        .where(store_owner_table.c.email == store_owner_email)
    return query


def get_suppliers_bound_to_product_query(product_id: StoreProductId):
    query = select(store_supplier_table) \
        .join(store_product_supplier_table,
              store_product_supplier_table.c.supplier_id == store_supplier_table.c.supplier_id) \
        .where(store_product_supplier_table.c.product_id == product_id)
    return query
