#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import select, func, distinct, and_
from sqlalchemy.sql import Select, Join, FromClause

from shop.adapter.shop_db import (
    shop_brand_table,
    shop_catalog_table,
    shop_collection_table,
    shop_product_collection_table,
    shop_product_supplier_table,
    shop_product_table,
    shop_product_view_cache_table,
    shop_supplier_table, shop_product_unit_table, shop_product_purchase_price_table, )
from shop.domain.entities.shop_product import ShopProduct
from shop.domain.entities.value_objects import ShopId, ShopProductId, GenericShopItemStatus, ShopCatalogId, \
    ShopSupplierId, SystemUserId


def check_shop_permission_query(shop_id: ShopId, current_user_id: SystemUserId,
                                from_clause: FromClause = None,
                                join_onclause_with_shop_table: Join = None):
    raise NotImplementedError
    # if as_join_clause and join_onclause_with_shop_table is None:
    #     raise Exception('join_onclause_with_shop_table must be specified in order to return a join clause')

    # if from_clause is not None and join_onclause_with_shop_table is None:
    #     raise Exception('join_onclause_with_shop_table must be specified in order to return a join clause')
    #
    # if from_clause is None:
    #     from_clause = select([shop_table.c.shop_id])
    #
    # query = from_clause.join(shop_users_table, shop_users_table.c.shop_id == shop_table.c.shop_id) \
    #     .where(and_(shop_users_table.c.user_id == current_user_id,
    #                 shop_users_table.c.shop_id == shop_id,
    #                 shop_table.c.status == ShopStatus.NORMAL,
    #                 shop_users_table.c.status == GenericShopItemStatus.NORMAL))
    #
    # return query


def count_catalogs_query_factory(shop_id: ShopId, active_only: bool = False) -> Select:
    q = select(func.count(distinct(shop_catalog_table.c.catalog_id))).where(
        shop_catalog_table.c.shop_id == shop_id)

    if active_only:
        q = q.where(shop_catalog_table.c.status == GenericShopItemStatus.NORMAL)

    return q


def list_shop_catalogs_query_factory(shop_id: ShopId) -> Select:
    return select([
        shop_catalog_table,
        shop_catalog_table.c.catalog_id,
        shop_catalog_table.c.title.label('catalog_title'),
        shop_catalog_table.c.default.label('is_default_catalog'),
        shop_catalog_table.c.image.label('catalog_image'),
        shop_catalog_table.c.status.label('catalog_status'),
    ]).where(shop_catalog_table.c.shop_id == shop_id)


def list_shop_collections_query_factory(shop_id: ShopId, catalog_id: ShopCatalogId) -> Select:
    query = select([
        shop_collection_table.c.collection_id,
        shop_collection_table.c.title,
        shop_collection_table.c.status.label('collection_status')
    ]).where(and_(shop_collection_table.c.catalog_id == catalog_id, shop_collection_table.c.shop_id == shop_id))

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
        ]).select_from(shop_product_table).select_from(shop_product_view_cache_table) \
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
        shop_catalog_table.c.status.label('catalog_status'),

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


def count_products_in_catalog_query_factory(shop_id: ShopId, catalog_id: ShopCatalogId) -> Select:
    q = count_products_query_factory(shop_id=shop_id).where(shop_product_table.c.catalog_id == catalog_id)
    return q


def get_shop_product_query_factory(shop_id: ShopId, product_id: ShopProductId) -> Select:
    """
    Return a Select query of selecting all data from shop_product_table by product_id

    :param shop_id:
    :param product_id: specified a product id
    :return: product row
    """
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
        .where(and_(shop_product_table.c.product_id == product_id, shop_product_table.c.shop_id == shop_id))

    return query


def get_shop_query_factory(store_owner_email: str):
    raise NotImplementedError
    # query = select(shop_table) \
    #     .join(shop_users_table, shop_table.c.shop_id == shop_users_table.c.shop_id) \
    #     .join(system_user_table, shop_users_table.c.user_id == system_user_table.c.user_id) \
    #     .where(system_user_table.c.email == store_owner_email)
    # return query


def list_shop_collections_bound_to_product_query_factory(shop_id: ShopId, product_id: ShopProductId):
    query = select([
        shop_collection_table.c.collection_id,
        shop_collection_table.c.title,
        shop_collection_table.c.status.label('collection_status')
    ]) \
        .join(shop_product_collection_table,
              shop_collection_table.c.collection_id == shop_product_collection_table.c.collection_id) \
        .join(shop_product_table, and_(shop_product_collection_table.c.product_id == shop_product_table.c.product_id,
                                       shop_product_table.c.catalog_id == shop_collection_table.c.catalog_id)) \
        .where(and_(
        shop_product_table.c.product_id == product_id,
        shop_collection_table.c.shop_id == shop_id
    ))

    return query


def count_suppliers_query_factory(shop_id: ShopId) -> Select:
    q = select([func.count(distinct(shop_supplier_table.c.supplier_id))]).where(
        shop_supplier_table.c.shop_id == shop_id)
    return q


def list_suppliers_bound_to_product_query(shop_id: ShopId, product_id: ShopProductId):
    query = select([
        shop_supplier_table,
        shop_supplier_table.c.status.label('supplier_status')
    ]) \
        .join(shop_product_supplier_table,
              shop_product_supplier_table.c.supplier_id == shop_supplier_table.c.supplier_id) \
        .join(shop_product_table,
              shop_product_table.c.product_id == shop_product_supplier_table.c.product_id) \
        .where(and_(shop_product_table.c.product_id == product_id, shop_product_table.c.shop_id == shop_id))
    return query


def count_products_in_supplier_query_factory(shop_id: ShopId, supplier_id: ShopSupplierId) -> Select:
    q = select([func.count(distinct(shop_product_table.c.product_id))]) \
        .join(shop_product_supplier_table,
              shop_product_table.c.product_id == shop_product_supplier_table.c.product_id) \
        .where(and_(shop_product_table.c.shop_id == shop_id, shop_product_supplier_table.c.supplier_id == supplier_id))
    return q


def list_units_bound_to_product_query_factory(shop_id: ShopId, product_id: ShopProductId):
    query = select([shop_product_unit_table]) \
        .join(shop_product_table,
              shop_product_table.c.product_id == shop_product_unit_table.c.product_id) \
        .where(and_(shop_product_unit_table.c.product_id == product_id, shop_product_table.c.shop_id == shop_id))

    return query


def list_purchase_prices_bound_to_product_query_factory(shop_id: ShopId, product_id: ShopProduct):
    """
    Return a query to list all the purchase price of a product.

    == FIX LATER ==
    In order to check permission of the current_user_id
    against the shop, join with `check_shop_permission_query`, as_join_clause must be specified as True, as well as
    need to specify join_onclause_with_shop_table as the join between shop_product_table and shop_table

    Ex: ```check_shop_permission_query(shop_id=shop_id, current_user_id=current_user_id, as_join_clause=True,
    join_onclause_with_shop_table=(shop_table.c.shop_id==shop_product_table.c.shop_id)
    ```
    == // FIX LATER ==

    :param shop_id: ShopId which contains the product
    :param product_id: the specified ProductId
    :return:
    """
    purchase_prices_query = select([
        shop_product_purchase_price_table,
        shop_supplier_table,
        shop_product_unit_table,
    ]).join(shop_supplier_table,
            shop_product_purchase_price_table.c.supplier_id == shop_supplier_table.c.supplier_id) \
        .join(shop_product_table,
              shop_product_purchase_price_table.c.product_id == shop_product_table.c.product_id) \
        .join(shop_product_unit_table,
              and_(shop_product_unit_table.c.unit_name == shop_product_purchase_price_table.c.unit,
                   shop_product_unit_table.c.product_id == shop_product_table.c.product_id)) \
        .where(and_(shop_product_table.c.product_id == product_id,
                    shop_product_table.c.shop_id == shop_id))

    return purchase_prices_query


def count_brands_query_factory(shop_id: ShopId) -> Select:
    q = select([func.count(distinct(shop_brand_table.c.brand_id))]) \
        .where(shop_brand_table.c.shop_id == shop_id)
    return q


def list_shop_brands_query_factory(shop_id: ShopId):
    query = select([shop_brand_table,
                    shop_brand_table.c.name.label('brand_name')]
                   ).where(shop_brand_table.c.shop_id == shop_id)

    return query
