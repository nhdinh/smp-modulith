#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import select, and_

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


def get_product_query_factory(store_id: StoreId, product_id: StoreProductId):
    query = select([
        StoreProduct,

        StoreCatalog.reference.label('catalog_reference'),
        StoreCatalog.title.label('catalog_title'),
        StoreCatalog.default.label('is_default_catalog'),
        StoreCatalog.image.label('catalog_image'),
        StoreCatalog.disabled.label('is_catalog_disabled'),

        StoreProductBrand,
        StoreProductBrand.name.label('brand_name'),
    ])

    query = query.join(StoreCatalog, StoreProduct._catalog)
    query = query.join(StoreProductBrand, StoreProduct._brand, isouter=True)
    query = query.join(Store, StoreProduct._store)

    query = query.where(and_(Store.store_id == store_id, StoreProduct.product_id == product_id))

    return query
