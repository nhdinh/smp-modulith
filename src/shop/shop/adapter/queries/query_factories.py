#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import select, func, distinct
from sqlalchemy.sql import Select

from shop.adapter.shop_db import (
    shop_brand_table,
    shop_catalog_table,
    shop_collection_table,
    shop_product_collection_table,
    shop_product_supplier_table,
    shop_product_table,
    shop_product_view_cache_table,
    shop_supplier_table,
)
from shop.domain.entities.value_objects import ShopId, ShopProductId


def shop_catalog_query_factory(store_id: ShopId) -> Select:
    return select([
        shop_catalog_table.c.catalog_id,
        shop_catalog_table.c.title.label('catalog_title'),
        shop_catalog_table.c.default.label('is_default_catalog'),
        shop_catalog_table.c.image.label('catalog_image'),
        shop_catalog_table.c.status.label('catalog_status'),
    ]).where(shop_catalog_table.c.shop_id == store_id)


def shop_collection_query_factory() -> Select:
    query = select([
        shop_collection_table.c.collection_id,
        shop_collection_table.c.title,
        shop_collection_table.c.status.label('collection_status')
    ])

    return query


def list_shop_products_query_factory(shop_id: ShopId, use_view_cache: bool = True) -> Select:
    """
    Create the base query to list all ShopProduct. This query is to select all fields from `product_table` and other
    related tables. In order to get further more table to join into the query, or apply some more filter, pagination
    parameters, then this query can be extended in demand.

    Beside, param of this factory, there is a `use_view_cache` flag. This flag is to indicate that the query will be
    select from the view_cache table or not. The view_cache table is to fasten the query performance but its tradeoff
    is that the data will not be fresh. There are maybe products yet to update into the view_cache.

    Set this flag to `True` in order to get data from view_cache. Else, set to `False`, the query will pull data from
    product table, then join with other relationship.

    :param shop_id: Id of the input shop
    :param use_view_cache: Use view_cache table or not. Default is True.
    :return: a base `Select` query
    """
    if use_view_cache:  # indicate if the query is select from view_cache, not real table
        query = select([
            shop_product_table,
            shop_product_view_cache_table
        ]) \
            .join(shop_product_view_cache_table,
                  shop_product_table.c.product_id == shop_product_view_cache_table.c.product_cache_id, isouter=True) \
            .where(shop_product_table.c.shop_id == shop_id)

        return query

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
        .where(shop_product_table.c.shop_id == shop_id)

    return query


def count_products_query_factory(shop_id: ShopId) -> Select:
    q = select([func.count(distinct(shop_product_table.c.product_id))]) \
        .where(shop_product_table.c.shop_id == shop_id)

    return q


def get_shop_product_query_factory(product_id: ShopProductId) -> Select:
    query = select([
        shop_product_table,

        shop_catalog_table.c.catalog_id,
        shop_catalog_table.c.title.label('catalog_title'),
        shop_catalog_table.c.default.label('is_default_catalog'),
        shop_catalog_table.c.image.label('catalog_image'),
        shop_catalog_table.c.status.label('catalog_status'),

        shop_brand_table.c.brand_id,
        shop_brand_table.c.name.label('brand_name'),
        shop_brand_table.c.logo,
    ]) \
        .join(shop_catalog_table, shop_product_table.c.catalog_id == shop_catalog_table.c.catalog_id) \
        .join(shop_brand_table, shop_product_table.c.brand_id == shop_brand_table.c.brand_id, isouter=True) \
        .where(shop_product_table.c.product_id == product_id)

    return query


def list_product_collections_query_factory(product_id: ShopProductId):
    query = shop_collection_query_factory() \
        .join(shop_product_collection_table,
              shop_product_table.c.product_id == shop_product_collection_table.c.product_id) \
        .join(shop_collection_table,
              shop_collection_table.c.collection_id == shop_product_collection_table.c.collection_id) \
        .where(shop_product_table.c.product_id == product_id)

    return query


def get_store_query_factory(store_owner_email: str):
    raise NotImplementedError
    # query = select(shop_table) \
    #     .join(shop_users_table, shop_table.c.shop_id == shop_users_table.c.shop_id) \
    #     .join(system_user_table, shop_users_table.c.user_id == system_user_table.c.user_id) \
    #     .where(system_user_table.c.email == store_owner_email)
    # return query


def get_suppliers_bound_to_product_query(product_id: ShopProductId):
    query = select([
        shop_supplier_table,
        shop_supplier_table.c.status.label('supplier_status')
    ]) \
        .join(shop_product_supplier_table,
              shop_product_supplier_table.c.supplier_id == shop_supplier_table.c.supplier_id) \
        .where(shop_product_supplier_table.c.product_id == product_id)
    return query
