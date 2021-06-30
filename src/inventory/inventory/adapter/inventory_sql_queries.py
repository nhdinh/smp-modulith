#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.orm import Query

from db_infrastructure import SqlQuery
from inventory.adapter.sql_query_common import sql_get_warehouse_id_by_owner
from inventory.application.inventory_queries import FetchAllProductsBalanceQuery, ProductBalanceResponseDto
from store.adapter.queries.query_common import sql_get_store_id_by_owner, sql_count_products_in_store
from web_app.serialization.dto import AuthorizedPaginationInputDto, PaginationOutputDto, paginate_response_factory


def fetch_inventory_product_balance_query_factory(warehouse_id) -> Query:
    pass


class SqlFetchAllProductsBalanceQuery(FetchAllProductsBalanceQuery, SqlQuery):
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[ProductBalanceResponseDto]:
        try:
            try:
                current_page = int(dto.page) if int(dto.page) > 0 else 1
                page_size = int(dto.page_size) if int(dto.page_size) > 0 else 10
            except:
                current_page = 1
                page_size = 10

            store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)
            warehouse_id = sql_get_warehouse_id_by_owner(warehouse_owner=dto.current_user, conn=self._conn)

            # get product counts
            product_counts = sql_count_products_in_store(store_id=store_id, conn=self._conn)

            # build product query
            query = fetch_inventory_product_balance_query_factory(warehouse_id=warehouse_id)
            query = query.limit(page_size).offset((current_page - 1) * page_size)

            # query product balance
            balance_records = self._conn.execute(query).all()

            return paginate_response_factory(
                current_page=current_page,
                page_size=page_size,
                total_items=product_counts,
                items=[
                    _row_to_product_balance_dto(row) for row in balance_records
                ]
            )
        except Exception as exc:
            raise exc
