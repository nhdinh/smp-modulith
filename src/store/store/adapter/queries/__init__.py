#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List

from sqlalchemy import select, func, join
from sqlalchemy.engine.row import RowProxy

from db_infrastructure import SqlQuery
from store.adapter import store_catalog_table, store_table
from store.adapter.store_db import store_catalog_cache_table, store_collection_table, store_owner_table
from store.application.queries.store_queries import FetchAllStoreCatalogsQuery, StoreCatalogResponseDto, \
    StoreCollectionResponseDto
from web_app.serialization.dto import PaginationOutputDto, AuthorizedPaginationInputDto, paginate_response_factory


def _row_to_catalog_dto(row: RowProxy, collections: List[RowProxy]) -> StoreCatalogResponseDto:
    return StoreCatalogResponseDto(
        catalog_id=row.catalog_id,
        store_id=row.store_id,
        reference=row.reference,
        display_name=row.display_name,
        system=row.system,
        disabled=row.disabled,
        collections=[
            _row_to_collection_dto(collection_row) for collection_row in collections
        ],
    )


def _row_to_collection_dto(row: RowProxy) -> StoreCollectionResponseDto:
    return StoreCollectionResponseDto(
        collection_id=row.collection_id,
        reference=row.reference,
        display_name=row.display_name,
        disabled=row.disabled,
    )


class SqlFetchAllStoreCatalogsQuery(FetchAllStoreCatalogsQuery, SqlQuery):
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreCatalogResponseDto]:
        current_page = dto.page if dto.page > 0 else 1

        store_id = self._conn.scalar(
            select(store_table.c.store_id).where(store_table.c.owner_email == dto.current_user)
        )

        # problem with the cache email from the `Store` table, we need to fetch the store by user_id
        if not store_id:
            store_id = self._conn.scalar(
                select(store_table.c.store_id) \
                    .join(store_owner_table, onclause=(store_table.c.owner == store_owner_table.c.id)) \
                    .where(store_owner_table.c.email == dto.current_user)
            )

        # count number of catalogs of this store
        catalog_count = self._conn.scalar(
            select([func.count()]) \
                .select_from(store_catalog_cache_table) \
                .where(store_catalog_cache_table.c.store_id == store_id)
        )

        # get all catalogs limit by page and offset
        get_all_catalogs_query = select([
            store_catalog_table.c.catalog_id,
            store_catalog_table.c.store_id,
            store_catalog_table.c.reference,
            store_catalog_table.c.display_name,
            store_catalog_table.c.system,
            store_catalog_table.c.disabled,
        ]) \
            .select_from(store_catalog_table) \
            .where(store_catalog_table.c.store_id == store_id) \
            .limit(dto.page_size).offset((current_page - 1) * dto.page_size)

        try:
            catalogs = self._conn.execute(get_all_catalogs_query).all()
            if not catalogs:
                # return None
                return paginate_response_factory(
                    current_page=dto.page,
                    page_size=dto.page_size,
                    total_items=catalog_count,
                    items=[]
                )

            # else, continue to load collections
            catalog_indices = set()
            for catalog in catalogs:
                catalog_indices.add(catalog.catalog_id)

            # get all collection with catalog_id in the list of catalog_indices
            collection_query = select([
                store_collection_table.c.collection_id,
                store_collection_table.c.store_id,
                store_collection_table.c.catalog_id,
                store_collection_table.c.reference,
                store_collection_table.c.display_name,
                store_collection_table.c.disabled,
            ], store_collection_table.c.catalog_id.in_(list(catalog_indices))) \
                .select_from(store_collection_table) \
                .where(store_collection_table.c.store_id == store_id)

            collections = self._conn.execute(collection_query).all()

            return paginate_response_factory(
                current_page=dto.page,
                page_size=dto.page_size,
                total_items=catalog_count,
                items=[
                    _row_to_catalog_dto(row, collections=[c for c in collections if c.catalog_id == row.catalog_id])
                    for row in catalogs]
            )
        except Exception as exc:
            raise exc
