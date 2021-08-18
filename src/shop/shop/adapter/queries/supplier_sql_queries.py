#!/usr/bin/env python
# -*- coding: utf-8 -*-
from itertools import groupby
from typing import Union

from sqlalchemy import select

from db_infrastructure.base import SqlQuery
from foundation.events import ThingGoneInBlackHoleError
from shop.adapter.queries.query_common import (

    sql_get_authorized_shop_id, sql_count_or_empty_return,
)
from shop.adapter.queries.query_factories import list_shop_products_query_factory, count_suppliers_query_factory, \
    count_products_in_supplier_query_factory
from shop.adapter.shop_db import shop_product_supplier_table, shop_product_table, shop_supplier_table, \
    shop_supplier_contact_table
from shop.application.queries.supplier_queries import (
    ListShopProductsBySupplierQuery,
    ListShopProductsBySupplierRequest,
    ListShopSuppliersQuery,
)
from shop.domain.dtos.product_dtos import ShopProductCompactedDto, _row_to_product_dto
from shop.domain.dtos.supplier_dtos import ShopSupplierDto, _row_to_supplier_dto, _row_to_supplier_contact_dto
from shop.domain.entities.value_objects import ExceptionMessages
from web_app.serialization.dto import BasePaginationAuthorizedRequest, PaginationTypedResponse, \
    paginate_response_factory, empty_list_response, SimpleListTypedResponse


class SqlListShopSuppliersQuery(ListShopSuppliersQuery, SqlQuery):
    def query(
            self, dto: BasePaginationAuthorizedRequest
    ) -> Union[PaginationTypedResponse[ShopSupplierDto], SimpleListTypedResponse]:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id, current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # get supplier counts
            suppliers_count_or_empty_result = sql_count_or_empty_return(count_suppliers_query_factory,
                                                                        conn=self._conn,
                                                                        shop_id=dto.shop_id)
            if not suppliers_count_or_empty_result:
                return empty_list_response()

            list_supplier_and_contacts_query = select([
                shop_supplier_table,
                shop_supplier_table.c.status.label('supplier_status'),
                shop_supplier_contact_table,
                shop_supplier_contact_table.c.status.label('contact_status')
            ]).select_from(shop_supplier_table).select_from(shop_supplier_contact_table) \
                .join(shop_supplier_contact_table,
                      shop_supplier_contact_table.c.supplier_id == shop_supplier_table.c.supplier_id) \
                .where(shop_supplier_table.c.shop_id == dto.shop_id)

            data_rows = self._conn.execute(list_supplier_and_contacts_query)
            data_rows = sorted(data_rows, key=lambda r: r.supplier_id)

            # TODO: Handle the Catalog Response Builder with this method

            response_items = []
            for supplier, contacts in groupby(data_rows, key=lambda x: _row_to_supplier_dto(x, [])):
                supplier.contacts = [_row_to_supplier_contact_dto(contact) for contact in list(contacts)]
                response_items.append(supplier)

            # build response items
            return paginate_response_factory(
                input_dto=dto,
                total_items=suppliers_count_or_empty_result,
                items=response_items
            )
        except Exception as exc:
            raise exc


class SqlListShopProductsBySupplierQuery(ListShopProductsBySupplierQuery, SqlQuery):
    def query(
            self, dto: ListShopProductsBySupplierRequest
    ) -> Union[PaginationTypedResponse[ShopProductCompactedDto], SimpleListTypedResponse]:
        try:
            valid_shop_id = sql_get_authorized_shop_id(shop_id=dto.shop_id, current_user_id=dto.current_user_id,
                                                       conn=self._conn)
            if not valid_shop_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_OWNERSHIP_NOT_FOUND)

            # count products of this supplier
            products_count = sql_count_or_empty_return(count_products_in_supplier_query_factory,
                                                       conn=self._conn,
                                                       shop_id=dto.shop_id,
                                                       supplier_id=dto.supplier_id)
            if not products_count:
                return empty_list_response()

            # build product query
            query = list_shop_products_query_factory(shop_id=dto.shop_id, use_view_cache=True) \
                .join(shop_product_supplier_table,
                      shop_product_table.c.product_id == shop_product_supplier_table.c.product_id) \
                .where(shop_product_supplier_table.c.supplier_id == dto.supplier_id)
            products = self._conn.execute(query).all()

            return paginate_response_factory(input_dto=dto, total_items=products_count,
                                             items=[_row_to_product_dto(row, compacted=True) for row in products])
        except Exception as exc:
            raise exc
