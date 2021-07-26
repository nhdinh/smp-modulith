#!/usr/bin/env python
# -*- coding: utf-8 -*-
from itertools import groupby

from sqlalchemy import select, and_, asc

from db_infrastructure.base import SqlQuery
from foundation.events import ThingGoneInBlackHoleError
from shop.adapter.queries.query_common import sql_get_authorized_shop_id
from shop.adapter.queries.query_factories import get_shop_product_query_factory, \
    list_shop_collections_bound_to_product_query_factory, \
    list_shop_products_query_factory, count_products_query_factory, list_suppliers_bound_to_product_query, \
    list_units_bound_to_product_query_factory, list_purchase_prices_bound_to_product_query_factory
from shop.adapter.shop_db import shop_product_unit_table, shop_product_tag_table, shop_product_purchase_price_table
from shop.application.queries.product_queries import GetShopProductQuery, GetShopProductRequest, ListShopProductsQuery, \
    ListShopProductsRequest, ListShopProductPurchasePricesRequest, ListShopProductPurchasePricesQuery, \
    ListUnitsByShopProductQuery, ListUnitsByShopProductRequest, ListShopSuppliersByProductQuery, \
    ListShopSuppliersByProductRequest, GetShopProductPurchasePriceQuery, GetShopProductPurchasePriceRequest, \
    GetShopProductLowestPurchasePriceQuery, GetShopProductLowestPurchasePriceRequest
from shop.domain.dtos.product_dtos import _row_to_product_dto, ShopProductCompactedDto, ShopProductPriceDto, \
    _row_to_product_price_dto
from shop.domain.dtos.product_unit_dtos import ShopProductUnitDto, _row_to_unit_dto
from shop.domain.dtos.supplier_dtos import ShopSupplierDto, _row_to_supplier_dto
from shop.domain.entities.value_objects import ExceptionMessages
from web_app.serialization.dto import PaginationTypedResponse, paginate_response_factory, SimpleListTypedResponse, \
    list_response_factory, empty_list_response


class SqlGetShopProductQuery(GetShopProductQuery, SqlQuery):
    def query(self, dto: GetShopProductRequest):
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id,
                                                       current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # get the product by id
            query = get_shop_product_query_factory(product_id=dto.product_id, shop_id=dto.shop_id)
            product = self._conn.execute(query).first()

            if product:
                # list collections
                list_collections_query = list_shop_collections_bound_to_product_query_factory(shop_id=dto.shop_id,
                                                                                              product_id=dto.product_id)
                collections = self._conn.execute(list_collections_query).all()

                # FIXME
                # list units
                list_units_query = select(shop_product_unit_table) \
                    .where(shop_product_unit_table.c.product_id == dto.product_id)
                units = self._conn.execute(list_units_query).all()

                # list suppliers
                list_suppliers_query = list_suppliers_bound_to_product_query(shop_id=dto.shop_id,
                                                                             product_id=dto.product_id)
                suppliers = self._conn.execute(list_suppliers_query).all()

                # list tags
                list_tags_query = select(shop_product_tag_table) \
                    .where(shop_product_tag_table.c.product_id == dto.product_id)
                tags = self._conn.execute(list_tags_query).all()
                return _row_to_product_dto(product, unit_rows=units, tag_rows=tags, collection_rows=collections,
                                           supplier_rows=suppliers, compacted=False)
            else:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_PRODUCT_NOT_FOUND)
        except Exception as exc:
            raise exc


class SqlListShopProductsQuery(ListShopProductsQuery, SqlQuery):
    def query(self, dto: ListShopProductsRequest) -> PaginationTypedResponse[ShopProductCompactedDto]:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id,
                                                       current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
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


class SqlListUnitsByShopProductQuery(ListUnitsByShopProductQuery, SqlQuery):
    def query(self, dto: ListUnitsByShopProductRequest) -> SimpleListTypedResponse[ShopProductUnitDto]:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id,
                                                       current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            units_query = list_units_bound_to_product_query_factory(shop_id=dto.shop_id, product_id=dto.product_id)
            units = self._conn.execute(units_query).all()

            items = [_row_to_unit_dto(r) for r in units] if units else []
            return list_response_factory(items=items)
        except Exception as exc:
            raise exc


class SqlListShopSuppliersByProductQuery(ListShopSuppliersByProductQuery, SqlQuery):
    def query(self, dto: ListShopSuppliersByProductRequest) -> SimpleListTypedResponse[ShopSupplierDto]:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id,
                                                       current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            suppliers_query = list_suppliers_bound_to_product_query(shop_id=dto.shop_id, product_id=dto.product_id)
            suppliers = self._conn.execute(suppliers_query).all()

            items = [_row_to_supplier_dto(r) for r in suppliers] if suppliers else []
            return list_response_factory(items=items)
        except Exception as exc:
            raise exc


class SqlListShopProductPurchasePricesQuery(ListShopProductPurchasePricesQuery, SqlQuery):
    def query(self, dto: ListShopProductPurchasePricesRequest) -> SimpleListTypedResponse[ShopProductPriceDto]:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id, current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            purchase_prices_query = list_purchase_prices_bound_to_product_query_factory(shop_id=dto.shop_id,
                                                                                        product_id=dto.product_id)
            data_rows = self._conn.execute(purchase_prices_query)

            if data_rows:
                data_rows = sorted(data_rows, key=lambda r: r.product_price_id)

            # make response_items
            response_items = dict()
            if not dto.group_by_supplier:
                for unit, others in groupby(data_rows, key=lambda x: x.unit):
                    response_items[unit] = [_row_to_product_price_dto(x) for x in others]
            else:
                for supplier_id, others in groupby(data_rows, key=lambda x: x.supplier_id):
                    response_items[supplier_id] = [_row_to_product_price_dto(x) for x in others]

            return list_response_factory(response_items)  # type:ignore
        except Exception as exc:
            raise exc


class SqlGetShopProductPurchasePriceQuery(GetShopProductPurchasePriceQuery, SqlQuery):
    def query(self, dto: GetShopProductPurchasePriceRequest) -> ShopProductPriceDto:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id, current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            purchase_price_query = list_purchase_prices_bound_to_product_query_factory(shop_id=dto.shop_id,
                                                                                       product_id=dto.product_id) \
                .where(and_(shop_product_purchase_price_table.c.unit == dto.unit,
                            shop_product_purchase_price_table.c.supplier_id == dto.supplier_id))
            price = self._conn.execute(purchase_price_query).first()

            return _row_to_product_price_dto(price) if price else empty_list_response()
        except Exception as exc:
            raise exc


class SqlGetShopProductLowestPurchasePriceQuery(GetShopProductLowestPurchasePriceQuery, SqlQuery):
    def query(self, dto: GetShopProductLowestPurchasePriceRequest) -> ShopProductPriceDto:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id, current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            purchase_price_query = list_purchase_prices_bound_to_product_query_factory(shop_id=dto.shop_id,
                                                                                       product_id=dto.product_id) \
                .where(shop_product_purchase_price_table.c.unit == dto.unit).order_by(
                asc(shop_product_purchase_price_table.c.price))
            price = self._conn.execute(purchase_price_query).first()

            return _row_to_product_price_dto(price) if price else empty_list_response()
        except Exception as exc:
            raise exc
