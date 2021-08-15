#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Union

from sqlalchemy import and_, select

from db_infrastructure.base import SqlQuery
from foundation.events import ThingGoneInBlackHoleError
from shop.adapter.queries.query_common import sql_get_authorized_shop_id, \
    sql_count_or_empty_return
from shop.adapter.queries.query_factories import (
    get_shop_catalog_query_factory,
    list_shop_products_query_factory,
    count_catalogs_query_factory, count_products_in_catalog_query_factory)
from shop.adapter.shop_db import shop_catalog_table, shop_collection_table, shop_product_table
from shop.application.queries.catalog_queries import (
    ListShopCatalogsQuery,
    ListShopCatalogsRequest,
    ListShopProductsByCatalogQuery,
    ListShopProductsByCatalogRequest, ListAllShopCatalogsQuery, ListAllShopCatalogRequest)
from shop.domain.dtos.catalog_dtos import ShopCatalogResponseDto, _row_to_catalog_dto
from shop.domain.dtos.product_dtos import ShopProductCompactedDto, _row_to_product_dto
from shop.domain.entities.value_objects import ExceptionMessages
from web_app.serialization.dto import PaginationTypedResponse, paginate_response_factory, empty_list_response, \
    SimpleListTypedResponse, list_response_factory


class SqlListShopCatalogsQuery(ListShopCatalogsQuery, SqlQuery):
    def query(self, dto: ListShopCatalogsRequest
              ) -> Union[PaginationTypedResponse[ShopCatalogResponseDto], SimpleListTypedResponse]:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id,
                                                       current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # count number of catalogs of this store
            catalog_count_or_empty_result = sql_count_or_empty_return(count_catalogs_query_factory,
                                                                      conn=self._conn,
                                                                      shop_id=dto.shop_id,
                                                                      active_only=False)
            if not catalog_count_or_empty_result:
                return empty_list_response()

            # get all catalogs limit by page and offset
            fetch_catalogs_query = get_shop_catalog_query_factory(shop_id=dto.shop_id) \
                .order_by(shop_catalog_table.c.created_at) \
                .limit(dto.page_size).offset((dto.current_page - 1) * dto.current_page)

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
                            shop_catalog_table.c.shop_id == dto.shop_id))

            collections = self._conn.execute(collection_query).all()

            return paginate_response_factory(
                input_dto=dto,
                total_items=catalog_count_or_empty_result,
                items=[
                    _row_to_catalog_dto(row, collections=[c for c in collections if c.catalog_id == row.catalog_id])
                    for row in catalogs]
            )
        except Exception as exc:
            raise exc


class SqlListAllShopCatalogsQuery(ListAllShopCatalogsQuery, SqlQuery):
    def query(self, dto: ListAllShopCatalogRequest) -> SimpleListTypedResponse[ShopCatalogResponseDto]:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id,
                                                       current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # get all catalogs limit by page and offset
            fetch_catalogs_query = get_shop_catalog_query_factory(shop_id=dto.shop_id) \
                .order_by(shop_catalog_table.c.created_at)

            catalogs = self._conn.execute(fetch_catalogs_query).all()

            return list_response_factory(items=[
                    _row_to_catalog_dto(row, collections=[])
                    for row in catalogs])
        except Exception as exc:
            raise exc


class SqlListShopProductsByCatalogQuery(ListShopProductsByCatalogQuery, SqlQuery):
    def query(
            self,
            dto: ListShopProductsByCatalogRequest
    ) -> Union[PaginationTypedResponse[ShopProductCompactedDto], SimpleListTypedResponse]:
        try:
            if not dto.catalog_id:
                raise ValueError(ExceptionMessages.INVALID_CATALOG_ID)

            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id,
                                                       current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # count row or return the empty result
            products_count_or_empty_result = sql_count_or_empty_return(count_products_in_catalog_query_factory,
                                                                       conn=self._conn,
                                                                       shop_id=dto.shop_id,
                                                                       catalog_id=dto.catalog_id)
            if not products_count_or_empty_result:
                return empty_list_response()

            # build product query
            query = list_shop_products_query_factory(shop_id=dto.shop_id, use_view_cache=dto.use_view_cache) \
                .where(shop_product_table.c.catalog_id == dto.catalog_id) \
                .limit(dto.page_size).offset(
                (dto.current_page - 1) * dto.page_size)

            # query products
            products = self._conn.execute(query).all()

            return paginate_response_factory(
                input_dto=dto,
                total_items=products_count_or_empty_result,
                items=[
                    _row_to_product_dto(row, compacted=True) for row in products
                ]
            )
        except Exception as exc:
            raise exc
