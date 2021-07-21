#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import and_, select

from db_infrastructure.base import SqlQuery
from foundation.events import ThingGoneInBlackHoleError
from shop.adapter.queries.query_common import sql_count_catalogs_in_shop, sql_verify_shop_id
from shop.adapter.queries.query_factories import (
    shop_catalog_query_factory,
    list_shop_products_query_factory,
    count_products_query_factory)
from shop.adapter.shop_db import shop_catalog_table, shop_collection_table, shop_product_table
from shop.application.queries.catalog_queries import (
    ListShopCatalogsQuery,
    ListShopCatalogsRequest,
    ListShopProductsByCatalogQuery,
    ListShopProductsByCatalogRequest)
from shop.domain.dtos.catalog_dtos import ShopCatalogResponseDto, _row_to_catalog_dto
from shop.domain.dtos.product_dtos import ShopProductCompactedDto, _row_to_product_dto
from shop.domain.entities.value_objects import ExceptionMessages
from web_app.serialization.dto import PaginationOutputDto, paginate_response_factory


class SqlListShopCatalogsQuery(ListShopCatalogsQuery, SqlQuery):
    def query(self, dto: ListShopCatalogsRequest) -> PaginationOutputDto[ShopCatalogResponseDto]:
        try:
            valid_store = sql_verify_shop_id(shop_id=dto.shop_id,
                                             partner_id=dto.partner_id,
                                             conn=self._conn)
            if not valid_store:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # count number of catalogs of this store
            shop_id = dto.shop_id
            catalog_count = sql_count_catalogs_in_shop(store_id=shop_id, conn=self._conn)
            if not catalog_count:
                return paginate_response_factory(
                    input_dto=dto,
                    total_items=catalog_count,
                    items=[]
                )

            # get all catalogs limit by page and offset
            fetch_catalogs_query = shop_catalog_query_factory(store_id=shop_id) \
                .order_by(shop_catalog_table.c.created_at) \
                .limit(dto.page_size).offset((dto.current_page - 1) * dto.page_size)

            catalogs = self._conn.execute(fetch_catalogs_query).all()

            # else, continue to load collection
            catalog_indices = set()
            for catalog in catalogs:
                catalog_indices.add(catalog.catalog_id)

            # get all collection with catalog_id in the list of catalog_indices
            collection_query = select([
                shop_collection_table,
                shop_collection_table.c.status.label('collection_status')
            ]).join(shop_catalog_table, shop_catalog_table.c.catalog_id == shop_collection_table.c.catalog_id) \
                .where(and_(shop_catalog_table.c.catalog_id.in_(catalog_indices),
                            shop_catalog_table.c.shop_id == shop_id))

            collections = self._conn.execute(collection_query).all()

            return paginate_response_factory(
                input_dto=dto,
                total_items=catalog_count,
                items=[
                    _row_to_catalog_dto(row, collections=[c for c in collections if c.catalog_id == row.catalog_id])
                    for row in catalogs]
            )
        except Exception as exc:
            raise exc


class SqlListShopProductsByCatalogQuery(ListShopProductsByCatalogQuery, SqlQuery):
    def query(self, dto: ListShopProductsByCatalogRequest) -> PaginationOutputDto[ShopProductCompactedDto]:
        try:
            valid_store = sql_verify_shop_id(shop_id=dto.shop_id,
                                             partner_id=dto.partner_id,
                                             conn=self._conn)
            if not valid_store:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # get product counts
            counting_q = count_products_query_factory(shop_id=dto.shop_id).where(
                shop_product_table.c.catalog_id == dto.catalog_id)
            product_counts = self._conn.scalar(counting_q)

            # build product query
            query = list_shop_products_query_factory(shop_id=dto.shop_id) \
                .where(shop_product_table.c.catalog_id == dto.catalog_id) \
                .limit(dto.pagination_entries_per_page).offset((dto.pagination_offset - 1) * dto.pagination_entries_per_page)

            # query products
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
