#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import select

from foundation.events import ThingGoneInBlackHoleError

from db_infrastructure.base import SqlQuery
from shop.adapter.queries.query_common import sql_verify_shop_id
from shop.adapter.queries.query_factories import get_shop_product_query_factory, list_product_collections_query_factory
from shop.application.queries.product_queries import GetShopProductQuery, GetShopProductRequest
from shop.domain.dtos.product_dtos import _row_to_product_dto
from shop.domain.entities.shop_product import ShopProduct
from shop.domain.entities.shop_product_tag import ShopProductTag
from shop.domain.entities.shop_product_unit import ShopProductUnit
from shop.domain.entities.value_objects import ExceptionMessages


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
                fetch_units_query = select(ShopProductUnit) \
                    .join(ShopProduct) \
                    .where(ShopProduct.product_id == product_id)
                units = self._conn.execute(fetch_units_query).all()

                # list tags
                fetch_tags_query = select(ShopProductTag) \
                    .join(ShopProduct) \
                    .where(ShopProduct.product_id == product_id)
                tags = self._conn.execute(fetch_tags_query).all()
                return _row_to_product_dto(product, unit_rows=units, tag_rows=tags, collection_rows=collections,
                                           compacted=False)
            else:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_PRODUCT_NOT_FOUND)
        except Exception as exc:
            raise exc
