#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import select

from foundation.events import ThingGoneInBlackHoleError

from db_infrastructure.base import SqlQuery
from shop.adapter.queries.query_common import (
    sql_count_all_products_by_supplier,
    sql_count_all_suppliers,
    sql_verify_shop_id,
)
from shop.adapter.queries.query_factories import list_shop_products_query_factory
from shop.adapter.shop_db import shop_product_supplier_table, shop_product_table, shop_supplier_table, \
    shop_supplier_contact_table
from shop.application.queries.supplier_queries import (
    ListShopProductsBySupplierQuery,
    ListShopProductsBySupplierRequest,
    ListShopSuppliersQuery,
)
from shop.domain.dtos.product_dtos import ShopProductCompactedDto, _row_to_product_dto
from shop.domain.dtos.supplier_dtos import StoreSupplierResponseDto, _row_to_supplier_dto
from shop.domain.entities.value_objects import ExceptionMessages
from web_app.serialization.dto import AuthorizedPaginationInputDto, PaginationOutputDto, paginate_response_factory


class SqlListShopSuppliersQuery(ListShopSuppliersQuery, SqlQuery):
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreSupplierResponseDto]:
        try:
            valid_store = sql_verify_shop_id(shop_id=dto.shop_id, partner_id=dto.partner_id,
                                             conn=self._conn)
            if not valid_store:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # get supplier counts
            count_suppliers = sql_count_all_suppliers(shop_id=dto.shop_id, conn=self._conn)

            # build supplier query
            query = select([
                shop_supplier_table,
                shop_supplier_table.c.status.label('supplier_status')
            ]).where(shop_supplier_table.c.shop_id == dto.shop_id)
            query = query.limit(dto.pagination_entries_per_page).offset(
                (dto.pagination_offset - 1) * dto.pagination_offset)

            # query products
            suppliers = self._conn.execute(query).all()
            supplier_indice = [supplier.supplier_id for supplier in suppliers]

            list_contact_query = select([shop_supplier_contact_table,
                                         shop_supplier_contact_table.c.status.label('contact_status')]).where(
                shop_supplier_contact_table.c.supplier_id.in_(supplier_indice))
            contacts = self._conn.execute(list_contact_query).all()

            s = [(supplier_row,
                  [contact_row for contact_row in contacts if contact_row.supplier_id == supplier_row.supplier_id]) for
                 supplier_row in suppliers]

            return paginate_response_factory(
                input_dto=dto,
                total_items=count_suppliers,
                items=[
                    _row_to_supplier_dto(supplier_row, []) for supplier_row in suppliers
                ]
            )
        except Exception as exc:
            raise exc


class SqlListShopProductsBySupplierQuery(ListShopProductsBySupplierQuery, SqlQuery):
    def query(self, dto: ListShopProductsBySupplierRequest) -> PaginationOutputDto[ShopProductCompactedDto]:
        try:
            valid_store = sql_verify_shop_id(shop_id=dto.shop_id, partner_id=dto.partner_id,
                                             conn=self._conn)
            if not valid_store:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # count products of this supplier
            count_products = sql_count_all_products_by_supplier(shop_id=dto.shop_id,
                                                                supplier_id=dto.supplier_id,
                                                                conn=self._conn)

            # build product query
            query = list_shop_products_query_factory(shop_id=dto.shop_id, use_view_cache=True) \
                .join(shop_product_supplier_table,
                      shop_product_table.c.product_id == shop_product_supplier_table.c.product_id) \
                .where(shop_product_supplier_table.c.supplier_id == dto.supplier_id)
            products = self._conn.execute(query).all()

            return paginate_response_factory(input_dto=dto, total_items=count_products,
                                             items=[_row_to_product_dto(row, compacted=True) for row in products])
        except Exception as exc:
            raise exc
