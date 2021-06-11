#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import select, func
from sqlalchemy.engine.row import RowProxy

from db_infrastructure import SqlQuery
from store.adapter import store_catalog_table, store_table
from store.adapter.store_db import store_catalog_cache_table
from store.application.queries.store_queries import FetchAllStoreCatalogsQuery, StoreCatalogResponseDto
from web_app.serialization.dto import PaginationOutputDto, AuthorizedPaginationInputDto, paginate_response_factory


def _row_to_catalog_dto(row: RowProxy) -> StoreCatalogResponseDto:
    return StoreCatalogResponseDto(
        reference=row.reference,
        display_name=row.display_name
    )


class SqlFetchAllStoreCatalogsQuery(FetchAllStoreCatalogsQuery, SqlQuery):
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreCatalogResponseDto]:
        store_id = self._conn.scalar(
            select(store_table.c.store_id).where(store_table.c.owner_email == dto.current_user)
        )

        # count rows
        total_catalogs = self._conn.scalar(
            select([func.count()]) \
                .select_from(store_catalog_cache_table) \
                .where(store_catalog_cache_table.c.store_id == store_id)
        )

        query = select([
            store_catalog_table.c.reference,
            store_catalog_table.c.display_name
        ]) \
            .select_from(store_catalog_table) \
            .where(store_catalog_table.c.store_id == store_id)

        try:
            result = self._conn.execute(query).all()
            if result:
                return paginate_response_factory(
                    current_page=dto.page,
                    page_size=dto.page_size,
                    total_items=total_catalogs,
                    items=[_row_to_catalog_dto(row) for row in result]
                )
        except Exception as exc:
            raise exc
