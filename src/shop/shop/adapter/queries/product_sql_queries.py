#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import select

from db_infrastructure.base import SqlQuery
from foundation.events import ThingGoneInBlackHoleError
from shop.adapter.queries.query_common import sql_verify_shop_id
from shop.adapter.queries.query_factories import get_shop_product_query_factory, \
    list_shop_collections_bound_to_product_query_factory, \
    list_shop_products_query_factory, count_products_query_factory, list_suppliers_bound_to_product_query, \
    list_units_bound_to_product_query
from shop.adapter.shop_db import shop_product_unit_table, shop_product_tag_table, shop_product_purchase_price_table
from shop.application.queries.product_queries import GetShopProductQuery, GetShopProductRequest, ListShopProductsQuery, \
    ListShopProductsRequest, ListShopProductPurchasePricesRequest, ListShopProductPurchasePricesQuery
from shop.domain.dtos.product_dtos import _row_to_product_dto, ShopProductCompactedDto, ShopProductPriceDto
from shop.domain.entities.value_objects import ExceptionMessages
from web_app.serialization.dto import PaginationOutputDto, paginate_response_factory, ListOutputDto


class SqlGetShopProductQuery(GetShopProductQuery, SqlQuery):
    def query(self, dto: GetShopProductRequest):
        try:
            valid_store = sql_verify_shop_id(shop_id=dto.shop_id,
                                             partner_id=dto.partner_id,
                                             conn=self._conn)
            if not valid_store:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # get the product by id
            product_id = dto.product_id
            query = get_shop_product_query_factory(product_id=product_id)
            product = self._conn.execute(query).first()

            if product:
                # list collections
                list_collections_query = list_shop_collections_bound_to_product_query_factory(product_id=product_id)
                collections = self._conn.execute(list_collections_query).all()

                # FIXME
                # list units
                list_units_query = select(shop_product_unit_table) \
                    .where(shop_product_unit_table.c.product_id == product_id)
                units = self._conn.execute(list_units_query).all()

                # list suppliers
                list_suppliers_query = list_suppliers_bound_to_product_query(product_id=product_id)
                suppliers = self._conn.execute(list_suppliers_query).all()

                # list tags
                list_tags_query = select(shop_product_tag_table) \
                    .where(shop_product_tag_table.c.product_id == product_id)
                tags = self._conn.execute(list_tags_query).all()
                return _row_to_product_dto(product, unit_rows=units, tag_rows=tags, collection_rows=collections,
                                           supplier_rows=suppliers, compacted=False)
            else:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_PRODUCT_NOT_FOUND)
        except Exception as exc:
            raise exc


class SqlListShopProductsQuery(ListShopProductsQuery, SqlQuery):
    def query(self, dto: ListShopProductsRequest) -> PaginationOutputDto[ShopProductCompactedDto]:
        try:
            valid_store = sql_verify_shop_id(shop_id=dto.shop_id,
                                             partner_id=dto.partner_id,
                                             conn=self._conn)
            if not valid_store:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # get product counts
            counting_q = count_products_query_factory(shop_id=dto.shop_id)
            product_counts = self._conn.scalar(counting_q)

            query = list_shop_products_query_factory(shop_id=dto.shop_id, use_view_cache=dto.use_view_cache) \
                .limit(dto.pagination_entries_per_page).offset(
                (dto.pagination_offset - 1) * dto.pagination_entries_per_page)

            products = self._conn.execute(query).all()

            return paginate_response_factory(
                input_dto=dto,
                total_items=product_counts,
                items=[
                    _row_to_product_dto(row, compacted=True) for row in products
                ]
            )
        except Exception as exc:
            raise exc


class SqlListShopProductPurchasePricesQuery(ListShopProductPurchasePricesQuery, SqlQuery):
    def query(self, dto: ListShopProductPurchasePricesRequest) -> ListOutputDto[ShopProductPriceDto]:
        try:
            valid_store = sql_verify_shop_id(shop_id=dto.shop_id, partner_id=dto.partner_id,
                                             conn=self._conn)
            if not valid_store:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # get the product by id
            query = get_shop_product_query_factory(product_id=dto.product_id)
            product = self._conn.execute(query).first()

            if product:
                suppliers_query = list_suppliers_bound_to_product_query(product_id=dto.product_id)
                suppliers = self._conn.execute(suppliers_query).all()

                units_query = list_units_bound_to_product_query(product_id=dto.product_id)
                units = self._conn.execute(units_query).all()

                prices_query = select(shop_product_purchase_price_table).where(
                    shop_product_purchase_price_table.c.product_id == dto.product_id)
                prices = self._conn.execute(prices_query)
        except Exception as exc:
            raise exc
