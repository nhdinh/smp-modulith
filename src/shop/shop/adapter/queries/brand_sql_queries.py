#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import desc

from db_infrastructure import SqlQuery
from foundation import ThingGoneInBlackHoleError
from shop.adapter.queries.query_common import sql_get_authorized_shop_id
from shop.adapter.queries.query_factories import list_shop_brands_query_factory, count_brands_query_factory
from shop.adapter.shop_db import shop_brand_table
from shop.application.queries.brand_queries import ListShopBrandsRequest, ListShopBrandsQuery, BrandOrderBy
from shop.domain.dtos.shop_brand_dtos import ShopBrandCompactedDto, _row_to_brand_dto
from shop.domain.entities.value_objects import ExceptionMessages, GenericShopItemStatus
from web_app.serialization.dto import SimpleListTypedResponse, list_response_factory, paginate_response_factory


class SqlListShopBrandsQuery(ListShopBrandsQuery, SqlQuery):
    def query(self, dto: ListShopBrandsRequest) -> SimpleListTypedResponse[ShopBrandCompactedDto]:
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
                list_brands_query = list_brands_query.where(shop_brand_table.c.status != GenericShopItemStatus.DISABLED)
                counting_q = counting_q.where(shop_brand_table.c.status != GenericShopItemStatus.DISABLED)

            # hide DELETED brands
            if not dto.display_deleted:
                list_brands_query = list_brands_query.where(shop_brand_table.c.status != GenericShopItemStatus.DELETED)
                counting_q = counting_q.where(shop_brand_table.c.status != GenericShopItemStatus.DELETED)

            # prepare the ordered column
            ordered_column = None
            if dto.order_by == BrandOrderBy.CREATED_DATE:
                ordered_column = shop_brand_table.c.created_at
            elif dto.order_by == BrandOrderBy.NAME:
                ordered_column = shop_brand_table.c.name
            elif dto.order_by == BrandOrderBy.PRODUCT_COUNT:
                ordered_column = shop_brand_table.c.product_count

            if ordered_column is not None:
                if dto.order_direction_descending:
                    list_brands_query = list_brands_query.order_by(desc(ordered_column))
                else:
                    list_brands_query = list_brands_query.order_by(ordered_column)

            # add limit and pagination
            list_brands_query = list_brands_query.limit(dto.page_size).offset((dto.current_page - 1) * dto.page_size)

            # execute the query
            brands = self._conn.execute(list_brands_query).all()
            brand_count = self._conn.scalar(counting_q)

            # build response
            response = paginate_response_factory(
                input_dto=dto,
                total_items=brand_count,
                items=[_row_to_brand_dto(brand) for brand in brands]
            )

            # TODO: Fix CodeSmell
            response = response.serialize()
            response.update({
                'display_disabled': dto.display_disabled,
                'display_deleted': dto.display_deleted,
                'order_by': dto.order_by if hasattr(dto, 'order_by') else None,
                'order_direction': ('DESC' if dto.order_direction_descending else 'ASC') if hasattr(dto,
                                                                                                    'order_direction_descending') else None,
            })

            return response  # type:ignore
        except Exception as exc:
            raise exc
