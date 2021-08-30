#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import desc, select

from db_infrastructure import SqlQuery
from foundation import ThingGoneInBlackHoleError
from shop.adapter.queries.query_common import sql_get_authorized_shop_id
from shop.adapter.queries.query_factories import list_shop_brands_query_factory, count_brands_query_factory
from shop.adapter.shop_db import shop_brand_table, shop_table
from shop.application.queries.brand_queries import ListShopBrandsRequest, ListShopBrandsQuery, BrandOrderOptions, \
    ListActiveShopBrandsQuery, ListActiveShopBrandsRequest, GetBrandsCacheHashQuery
from shop.domain.dtos.shop_brand_dtos import ShopBrandDto, ShopBrandShortDto
from shop.domain.entities.value_objects import ExceptionMessages, GenericShopItemStatus
from web_app.serialization.dto import paginate_response_factory, PaginationTypedResponse, row_proxy_to_dto, \
    SimpleListTypedResponse, list_response_factory, BaseAuthorizedShopUserRequest, GeneralHashDto


class SqlListShopBrandsQuery(ListShopBrandsQuery, SqlQuery):
    order_columns = {
        BrandOrderOptions.CREATED_DATE: shop_brand_table.c.created_at,
        BrandOrderOptions.NAME: shop_brand_table.c.name,
        BrandOrderOptions.PRODUCT_COUNT: shop_brand_table.c.product_count
    }

    def query(self, dto: ListShopBrandsRequest) -> PaginationTypedResponse[ShopBrandDto]:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id, current_user_id=dto.current_user_id,
                                                       conn=self._conn)

            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # prepare the counting query
            counting_q = count_brands_query_factory(shop_id=dto.shop_id)

            # prepare the data query
            list_brands_query = list_shop_brands_query_factory(shop_id=dto.shop_id)

            # hide DISABLED brands
            if not dto.display_disabled:
                list_brands_query = list_brands_query.filter(
                    shop_brand_table.c.status != GenericShopItemStatus.DISABLED)
                counting_q = counting_q.filter(shop_brand_table.c.status != GenericShopItemStatus.DISABLED)

            # hide DELETED brands
            if not dto.display_deleted:
                list_brands_query = list_brands_query.filter(shop_brand_table.c.status != GenericShopItemStatus.DELETED)
                counting_q = counting_q.filter(shop_brand_table.c.status != GenericShopItemStatus.DELETED)

            # prepare the ordered column
            if dto.order_by in self.order_columns:
                if dto.order_direction_descending:
                    list_brands_query = list_brands_query.order_by(desc(self.order_columns[dto.order_by]))
                else:
                    list_brands_query = list_brands_query.order_by(self.order_columns[dto.order_by])

            # add limit and pagination
            list_brands_query = list_brands_query.limit(dto.page_size).offset((dto.current_page - 1) * dto.page_size)

            # execute the query
            brands = self._conn.execute(list_brands_query).all()
            brand_count = self._conn.scalar(counting_q)

            # build response
            response = paginate_response_factory(
                input_dto=dto,
                total_items=brand_count,
                items=row_proxy_to_dto(brands, ShopBrandDto)
            )

            return response  # type:ignore
        except Exception as exc:
            raise exc


class SqlListAllShopBrandsQuery(ListActiveShopBrandsQuery, SqlQuery):
    def query(self, dto: ListActiveShopBrandsRequest) -> SimpleListTypedResponse[ShopBrandShortDto]:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id,
                                                       current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # get all catalogs limit by page and offset
            fetch_brands_query = list_shop_brands_query_factory(shop_id=dto.shop_id) \
                .filter(shop_brand_table.c.status == GenericShopItemStatus.NORMAL) \
                .order_by(shop_brand_table.c.name) \

            brands = self._conn.execute(fetch_brands_query).all()

            return list_response_factory(items=row_proxy_to_dto(brands, ShopBrandShortDto))
        except Exception as exc:
            raise exc


class SqlGetBrandsCacheHashQuery(GetBrandsCacheHashQuery, SqlQuery):
    def query(self, dto: BaseAuthorizedShopUserRequest) -> GeneralHashDto:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id,
                                                       current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            shop_qry = select(shop_table.c.version).filter(shop_table.c.shop_id == dto.shop_id)
            shop_data = self._conn.scalar(shop_qry)
            brand_hash = hash(shop_data)

            return GeneralHashDto(brand_hash)
        except Exception as exc:
            raise exc
