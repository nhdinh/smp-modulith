#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import select

from db_infrastructure import SqlQuery
from store.adapter.queries.query_common import sql_verify_shop_id_with_partner_id
from store.adapter.queries.query_factories import get_product_query_factory, list_product_collections_query_factory
from store.application.queries.dtos.store_product_dto import _row_to_product_dto
from store.application.queries.get_shop_product_query import GetShopProductRequest, GetShopProductQuery
from store.application.usecases.const import ThingGoneInBlackHoleError, ExceptionMessages
from store.domain.entities.shop_unit import ShopProductUnit
from store.domain.entities.store_product import ShopProduct
from store.domain.entities.store_product_tag import ShopProductTag


class SqlGetShopProductQuery(GetShopProductQuery, SqlQuery):
    def query(self, dto: GetShopProductRequest, from_cache: bool = True):
        try:
            valid_store = sql_verify_shop_id_with_partner_id(shop_id=dto.shop_id, partner_id=dto.partner_id,
                                                             conn=self._conn)
            if not valid_store:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # get the product by id
            product_id = dto.product_id
            query = get_product_query_factory(product_id=product_id)
            product = self._conn.execute(query).first()

            if product:
                # list collections
                list_collections_query = list_product_collections_query_factory(product_id=product_id)
                collections = self._conn.execute(list_collections_query).all()

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
                raise ThingGoneInBlackHoleError(ExceptionMessages.STORE_PRODUCT_NOT_FOUND)
        except Exception as exc:
            raise exc
