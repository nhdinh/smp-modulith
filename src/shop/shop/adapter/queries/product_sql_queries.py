#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import select, desc

from db_infrastructure.base import SqlQuery
from foundation.events import ThingGoneInBlackHoleError
from shop.adapter.queries.query_common import sql_get_authorized_shop_id
from shop.adapter.queries.query_factories import get_shop_product_query_factory, \
    list_shop_collections_bound_to_product_query_factory, \
    list_shop_products_query_factory, count_products_query_factory, list_suppliers_bound_to_product_query, \
    list_units_bound_to_product_query_factory
from shop.adapter.shop_db import shop_product_tag_table, \
    shop_product_table, shop_catalog_table, shop_brand_table, shop_product_unit_table
from shop.application.queries.product_queries import GetShopProductQuery, GetShopProductRequest, ListShopProductsQuery, \
    ListShopProductsRequest, ListUnitsByShopProductQuery, ListUnitsByShopProductRequest, \
    ListShopSuppliersByProductQuery, \
    ListShopSuppliersByProductRequest, ProductOrderOptions
from shop.domain.dtos.product_dtos import _row_to_product_dto, ShopProductDto
from shop.domain.dtos.product_unit_dtos import ShopProductUnitDto, _row_to_unit_dto
from shop.domain.dtos.supplier_dtos import ShopSupplierDto, _row_to_supplier_dto
from shop.domain.entities.value_objects import ExceptionMessages, GenericShopItemStatus
from web_app.serialization.dto import PaginationTypedResponse, paginate_response_factory, SimpleListTypedResponse, \
    list_response_factory


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
                                                                                              product_id=product.product_id)
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
                response = _row_to_product_dto(product, unit_rows=units, tag_rows=tags, collection_rows=collections,
                                               supplier_rows=suppliers)

                return response
            else:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_PRODUCT_NOT_FOUND)
        except Exception as exc:
            raise exc


class SqlListShopProductsQuery(ListShopProductsQuery, SqlQuery):
    order_columns = {
        ProductOrderOptions.TITLE: shop_product_table.c.title,
        ProductOrderOptions.CREATED_DATE: shop_product_table.c.created_at,
        ProductOrderOptions.CATALOG_TITLE: shop_catalog_table.c.title,
        ProductOrderOptions.BRAND_NAME: shop_brand_table.c.name,
        ProductOrderOptions.CURRENT_STOCK: shop_product_table.c.current_stock,
    }

    def query(self, dto: ListShopProductsRequest) -> PaginationTypedResponse[ShopProductDto]:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id,
                                                       current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # get product counts
            counting_q = count_products_query_factory(shop_id=dto.shop_id)

            # disable use view cache when the result is ordered
            _use_view_cache = dto.use_view_cache
            if dto.order_by:
                _use_view_cache = False

            # prepare the query
            query = list_shop_products_query_factory(shop_id=dto.shop_id, use_view_cache=_use_view_cache) \
                .where(shop_catalog_table.c.status == GenericShopItemStatus.NORMAL)

            # hide DISABLED products
            if not dto.display_disabled:
                query = query.where(shop_product_table.c.status != GenericShopItemStatus.DISABLED)
                counting_q = counting_q.where(shop_product_table.c.status != GenericShopItemStatus.DISABLED)

            # hide DELETED products
            if not dto.display_deleted:
                query = query.where(shop_product_table.c.status != GenericShopItemStatus.DELETED)
                counting_q = counting_q.where(shop_product_table.c.status != GenericShopItemStatus.DELETED)

            # ordering the data result
            if dto.order_by in self.order_columns:
                if dto.order_direction_descending:
                    query = query.order_by(desc(self.order_columns[dto.order_by]))
                else:
                    query = query.order_by(self.order_columns[dto.order_by])

            # add limit and pagination
            query = query.limit(dto.page_size).offset((dto.current_page - 1) * dto.page_size)

            # execute the query
            products = self._conn.execute(query).all()
            product_counts = self._conn.scalar(counting_q)

            # build response
            response = paginate_response_factory(
                input_dto=dto,
                total_items=product_counts,
                # items=row_proxy_to_dto(products, ShopProductDto),
                items=[_row_to_product_dto(p) for p in products]
            )

            return response
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
