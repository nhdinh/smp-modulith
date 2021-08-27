#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Union

from sqlalchemy import and_, select, desc

from db_infrastructure.base import SqlQuery
from foundation.events import ThingGoneInBlackHoleError
from shop.adapter.queries.query_common import sql_get_authorized_shop_id, \
    sql_count_or_empty_return
from shop.adapter.queries.query_factories import (
    list_shop_catalogs_query_factory,
    list_shop_products_query_factory,
    count_catalogs_query_factory, count_products_in_catalog_query_factory)
from shop.adapter.shop_db import shop_catalog_table, shop_collection_table, shop_product_table
from shop.application.queries.catalog_queries import (
    ListShopCatalogsQuery,
    ListShopCatalogsRequest,
    ListShopProductsByCatalogQuery,
    ListShopProductsByCatalogRequest, ListAllShopCatalogsQuery, ListAllShopCatalogRequest, ShopCatalogOrderOptions)
from shop.domain.dtos.catalog_dtos import ShopCatalogResponseDto, _row_to_catalog_dto
from shop.domain.dtos.product_dtos import ShopProductCompactedDto, _row_to_product_dto
from shop.domain.entities.value_objects import ExceptionMessages, GenericShopItemStatus
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
            counting_qry = count_catalogs_query_factory(shop_id=dto.shop_id)

            # get all catalogs limit by page and offset
            list_catalog_qry = list_shop_catalogs_query_factory(shop_id=dto.shop_id) \
                .order_by(shop_catalog_table.c.created_at) \
                .limit(dto.page_size).offset((dto.current_page - 1) * dto.current_page)

            # filter by display_disabled
            if not dto.display_disabled:
                counting_qry = counting_qry.filter(shop_catalog_table.c.status != GenericShopItemStatus.DISABLED)
                list_catalog_qry = list_catalog_qry.filter(
                    shop_catalog_table.c.status != GenericShopItemStatus.DISABLED)

            # filter by display_disabled
            if not dto.display_deleted:
                counting_qry = counting_qry.filter(shop_catalog_table.c.status != GenericShopItemStatus.DELETED)
                list_catalog_qry = list_catalog_qry.filter(shop_catalog_table.c.status != GenericShopItemStatus.DELETED)

            # get the counting_qry
            catalog_count = self._conn.scalar(counting_qry)

            # order the result
            if not catalog_count:
                # return the data here
                return paginate_response_factory(input_dto=dto, total_items=catalog_count, items=[])

            # else, order the result
            ordered_column = None
            if dto.order_by == ShopCatalogOrderOptions.CREATED_DATE:
                ordered_column = shop_catalog_table.c.created_at
            elif dto.order_by == ShopCatalogOrderOptions.UPDATED_DATE:
                ordered_column = shop_catalog_table.c.updated_at
            elif dto.order_by == ShopCatalogOrderOptions.PRODUCT_COUNT:
                ordered_column = shop_catalog_table.c.product_count
            elif dto.order_by == ShopCatalogOrderOptions.COLLECTION_COUNT:
                ordered_column = shop_catalog_table.c.collection_count
            elif dto.order_by == ShopCatalogOrderOptions.DEFAULT:
                ordered_column = shop_catalog_table.c.default

            if ordered_column is not None:
                if dto.order_direction_descending:
                    list_catalog_qry = list_catalog_qry.order_by(desc(ordered_column))
                else:
                    list_catalog_qry = list_catalog_qry.order_by(ordered_column)

            catalogs = self._conn.execute(list_catalog_qry).all()

            return paginate_response_factory(
                input_dto=dto,
                total_items=catalog_count,
                items=[_row_to_catalog_dto(row) for row in catalogs]
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
            fetch_catalogs_query = list_shop_catalogs_query_factory(shop_id=dto.shop_id) \
                .order_by(shop_catalog_table.c.created_at)

            catalogs = self._conn.execute(fetch_catalogs_query).all()

            return list_response_factory(items=[
                _row_to_catalog_dto(row)
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
