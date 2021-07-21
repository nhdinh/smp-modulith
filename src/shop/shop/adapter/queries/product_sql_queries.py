#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import select

from db_infrastructure.base import SqlQuery
from foundation.events import ThingGoneInBlackHoleError
from shop.adapter.queries.query_common import sql_verify_shop_id
from shop.adapter.queries.query_factories import get_shop_product_query_factory, list_product_collections_query_factory, \
    list_shop_products_query_factory, count_products_query_factory
from shop.adapter.shop_db import shop_product_unit_table, shop_product_tag_table
from shop.application.queries.product_queries import GetShopProductQuery, GetShopProductRequest, ListShopProductsQuery, \
    ListShopProductsRequest
from shop.domain.dtos.product_dtos import _row_to_product_dto, ShopProductCompactedDto
from shop.domain.entities.value_objects import ExceptionMessages
from web_app.serialization.dto import PaginationOutputDto, paginate_response_factory


class SqlGetShopProductQuery(GetShopProductQuery, SqlQuery):
    def query(self, dto: GetShopProductRequest, use_view_cache: bool = False):
        try:
            valid_store = sql_verify_shop_id(shop_id=dto.shop_id, partner_id=dto.partner_id,
                                             conn=self._conn)
            if not valid_store:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # get the product by id
            product_id = dto.product_id
            query = get_shop_product_query_factory(product_id=product_id)
            product = self._conn.execute(query).first()

            if product:
                # list collections
                list_collections_query = list_product_collections_query_factory(product_id=product_id)
                collections = self._conn.execute(list_collections_query).all()

                # FIXME
                # list units
                fetch_units_query = select(shop_product_unit_table) \
                    .where(shop_product_unit_table.c.product_id == product_id)
                units = self._conn.execute(fetch_units_query).all()

                # list tags
                fetch_tags_query = select(shop_product_tag_table) \
                    .where(shop_product_tag_table.c.product_id == product_id)
                tags = self._conn.execute(fetch_tags_query).all()
                return _row_to_product_dto(product, unit_rows=units, tag_rows=tags, collection_rows=collections,
                                           compacted=False)
            else:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_PRODUCT_NOT_FOUND)
        except Exception as exc:
            raise exc


class SqlListShopProductsQuery(ListShopProductsQuery, SqlQuery):
    def query(self, dto: ListShopProductsRequest, use_view_cache: bool = True) -> PaginationOutputDto[
        ShopProductCompactedDto]:
        try:
            valid_store = sql_verify_shop_id(shop_id=dto.shop_id, partner_id=dto.partner_id,
                                             conn=self._conn)
            if not valid_store:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # get product counts
            counting_q = count_products_query_factory(shop_id=dto.shop_id)
            product_counts = self._conn.scalar(counting_q)

            query = list_shop_products_query_factory(shop_id=dto.shop_id) \
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
