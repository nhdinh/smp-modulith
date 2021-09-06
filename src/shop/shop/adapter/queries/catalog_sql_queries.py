#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Union

from sqlalchemy import desc, and_, select

from db_infrastructure.base import SqlQuery
from foundation.events import ThingGoneInBlackHoleError
from shop.adapter.queries.query_common import sql_get_authorized_shop_id, \
    sql_count_or_empty_return
from shop.adapter.queries.query_factories import (
    list_shop_catalogs_query_factory,
    list_shop_products_query_factory,
    count_catalogs_query_factory, count_products_in_catalog_query_factory, list_shop_collections_query_factory)
from shop.adapter.shop_db import shop_catalog_table, shop_product_table, shop_collection_table, shop_table
from shop.application.queries.catalog_queries import (
    ListShopCatalogsQuery,
    ListShopCatalogsRequest,
    ListShopProductsByCatalogQuery,
    ListShopProductsByCatalogRequest, ListActiveShopCatalogsQuery, ListActiveShopCatalogsRequest,
    ShopCatalogOrderOptions, ListShopCollectionsByCatalogRequest, ListShopCollectionsByCatalogQuery,
    ListActiveShopCollectionsByCatalogQuery, ListActiveShopCollectionsByCatalogRequest, GetCollectionCacheHashQuery,
    GetCollectionCacheHashRequest)
from shop.domain.dtos.catalog_dtos import ShopCatalogDto, ShopCatalogShortDto
from shop.domain.dtos.collection_dtos import ShopCollectionDto, ShopCollectionShortDto
from shop.domain.dtos.product_dtos import ShopProductDto
from shop.domain.entities.shop_collection import ShopCollection
from shop.domain.entities.value_objects import ExceptionMessages, GenericShopItemStatus
from web_app.serialization.dto import PaginationTypedResponse, paginate_response_factory, empty_list_response, \
    SimpleListTypedResponse, list_response_factory, row_proxy_to_dto, GeneralHashDto


class SqlListShopCatalogsQuery(ListShopCatalogsQuery, SqlQuery):
    order_columns = {
        ShopCatalogOrderOptions.CREATED_DATE: shop_catalog_table.c.created_at,
        ShopCatalogOrderOptions.UPDATED_DATE: shop_catalog_table.c.updated_at,
        ShopCatalogOrderOptions.DEFAULT: shop_catalog_table.c.default,
        ShopCatalogOrderOptions.PRODUCT_COUNT: shop_catalog_table.c.product_count,
        ShopCatalogOrderOptions.COLLECTION_COUNT: shop_catalog_table.c.collection_count,
    }

    def query(self, dto: ListShopCatalogsRequest
              ) -> Union[PaginationTypedResponse[ShopCatalogDto], SimpleListTypedResponse]:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id,
                                                       current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # count number of catalogs of this store
            counting_qry = count_catalogs_query_factory(shop_id=dto.shop_id)

            # get all catalogs limit by page and offset
            list_catalog_qry = list_shop_catalogs_query_factory(shop_id=dto.shop_id)

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
            if dto.order_by in self.order_columns.keys():
                if dto.order_direction_descending:
                    list_catalog_qry = list_catalog_qry.order_by(desc(self.order_columns[dto.order_by]))
                else:
                    list_catalog_qry = list_catalog_qry.order_by(self.order_columns[dto.order_by])

            # pagination
            list_catalog_qry = list_catalog_qry.limit(dto.page_size).offset((dto.current_page - 1) * dto.current_page)

            catalogs = self._conn.execute(list_catalog_qry).all()

            return paginate_response_factory(
                input_dto=dto,
                total_items=catalog_count,
                items=row_proxy_to_dto(catalogs, ShopCatalogDto)
            )
        except Exception as exc:
            raise exc


class SqlListAllShopCatalogsQuery(ListActiveShopCatalogsQuery, SqlQuery):
    def query(self, dto: ListActiveShopCatalogsRequest) -> SimpleListTypedResponse[ShopCatalogShortDto]:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id,
                                                       current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # get all catalogs limit by page and offset
            fetch_catalogs_query = list_shop_catalogs_query_factory(shop_id=dto.shop_id) \
                .filter(shop_catalog_table.c.status == GenericShopItemStatus.NORMAL) \
                .order_by(shop_catalog_table.c.title)

            catalogs = self._conn.execute(fetch_catalogs_query).all()

            return list_response_factory(items=row_proxy_to_dto(catalogs, ShopCatalogShortDto))
        except Exception as exc:
            raise exc


class SqlListShopProductsByCatalogQuery(ListShopProductsByCatalogQuery, SqlQuery):
    def query(
            self,
            dto: ListShopProductsByCatalogRequest
    ) -> Union[PaginationTypedResponse[ShopProductDto], SimpleListTypedResponse]:
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
                items=row_proxy_to_dto(products, ShopProductDto)
            )
        except Exception as exc:
            raise exc


class SqlListShopCollectionsByCatalogQuery(ListShopCollectionsByCatalogQuery, SqlQuery):
    def query(self, dto: ListShopCollectionsByCatalogRequest) -> PaginationTypedResponse[ShopCollectionDto]:
        try:
            if not dto.catalog_id:
                raise ValueError(ExceptionMessages.INVALID_CATALOG_ID)

            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id,
                                                       current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            raise NotImplementedError
        except Exception as exc:
            raise exc


class SqlListAllShopCollectionsByCatalogQuery(ListActiveShopCollectionsByCatalogQuery, SqlQuery):
    def query(self, dto: ListActiveShopCollectionsByCatalogRequest) -> SimpleListTypedResponse[ShopCollectionShortDto]:
        try:
            if not dto.catalog_id:
                raise ValueError(ExceptionMessages.INVALID_CATALOG_ID)

            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id,
                                                       current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # get all collections
            fetch_collections_query = list_shop_collections_query_factory(shop_id=dto.shop_id,
                                                                          catalog_id=dto.catalog_id) \
                .where(shop_collection_table.c.status == GenericShopItemStatus.NORMAL) \
                .order_by(shop_collection_table.c.title)

            collections = self._conn.execute(fetch_collections_query).all()

            return list_response_factory(items=row_proxy_to_dto(collections, ShopCollectionShortDto))
        except Exception as exc:
            raise exc


class SqlGetCollectionCacheHashQuery(GetCollectionCacheHashQuery, SqlQuery):
    def query(self, dto: GetCollectionCacheHashRequest) -> GeneralHashDto:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id,
                                                       current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            shop_qry = select(shop_table.c.version).filter(shop_table.c.shop_id == dto.shop_id)
            shop_data = self._conn.scalar(shop_qry)
            catalog_hash = hash(shop_data)

            return GeneralHashDto(catalog_hash)
        except Exception as exc:
            raise exc
