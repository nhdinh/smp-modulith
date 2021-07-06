#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import select, and_

from store.adapter.store_db import store_product_table, store_brand_table, store_catalog_table, store_collection_table, \
    store_product_collection_table
from store.domain.entities.store import StoreId, Store
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_product import StoreProduct, StoreProductId
from store.domain.entities.store_product_brand import StoreProductBrand


def list_store_product_query_factory(store_id: StoreId):
    query = select([
        StoreProduct,
        # StoreCatalog.reference.label('catalog_reference'),
        # StoreCatalog.title.label('catalog_title'),

        # StoreCollection.reference.label('collection_reference'),
        # StoreCollection.title.label('collection_title'),

        # StoreProductBrand.name.label('brand_name'),
        StoreCatalog.title.label('catalog_title'),
        StoreCatalog.reference.label('catalog_reference'),
        StoreProductBrand.name.label('brand_name'),
        StoreProductBrand,

        # StoreProductUnit
    ]) \
        .join(StoreCatalog, StoreProduct._catalog) \
        .join(StoreProductBrand, StoreProduct._brand, isouter=True) \
        .join(Store, StoreCatalog._store).where(Store.store_id == store_id)

    return query


def get_product_query_factory(product_id: StoreProductId):
    query = select([
        store_product_table,

        store_catalog_table.c.catalog_id,
        store_catalog_table.c.reference.label('catalog_reference'),
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


def get_product_collections_query_factory(product_id: StoreProductId):
    query = select([
        store_collection_table.c.collection_id,
        store_collection_table.c.reference,
        store_collection_table.c.title,
        store_collection_table.c.disabled.label('is_collection_disabled')
    ]) \
        .join(store_product_collection_table,
              store_product_table.c.product_id == store_product_collection_table.c.product_id) \
        .join(store_collection_table,
              store_collection_table.c.collection_id == store_product_collection_table.c.collection_id) \
        .where(store_product_table.c.product_id == product_id)

    return query
