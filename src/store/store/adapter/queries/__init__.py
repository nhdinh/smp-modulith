#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List

from sqlalchemy import select
from sqlalchemy.engine.row import RowProxy

from db_infrastructure import SqlQuery
from store.adapter import store_catalog_table
from store.adapter.queries.query_common import sql_fetch_store_by_owner, sql_count_catalog_from_store, \
    sql_count_collection_from_catalog, sql_fetch_catalog_by_reference
from store.adapter.store_db import store_collection_table
from store.application.queries.store_queries import FetchAllStoreCatalogsQuery, StoreCatalogResponseDto, \
    StoreCollectionResponseDto, FetchAllStoreCollectionsQuery, FetchAllStoreProductsQuery, StoreProductResponseDto
from store.domain.entities.value_objects import StoreCollectionReference, StoreCatalogReference
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
        default=row.default,
    )


class SqlFetchAllStoreCatalogsQuery(FetchAllStoreCatalogsQuery, SqlQuery):
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreCatalogResponseDto]:
        current_page = dto.page if dto.page > 0 else 1

        store_id = sql_fetch_store_by_owner(store_owner=dto.current_user, conn=self._conn)

        # count number of catalogs of this store
        catalog_count = sql_count_catalog_from_store(store_id=store_id, conn=self._conn)

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

            # else, continue to load collection
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
                store_collection_table.c.default,
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


class SqlFetchAllStoreCollectionsQuery(FetchAllStoreCollectionsQuery, SqlQuery):
    def query(self, catalog_reference: StoreCatalogReference, dto: AuthorizedPaginationInputDto):
        try:
            current_page = dto.page if dto.page else 1

            store_id = sql_fetch_store_by_owner(store_owner=dto.current_user, conn=self._conn)
            catalog_id = sql_fetch_catalog_by_reference(catalog_reference=catalog_reference, store_id=store_id,
                                                        conn=self._conn)
            collection_count = sql_count_collection_from_catalog(store_id=store_id, catalog_id=catalog_id,
                                                                 conn=self._conn)

            collection_query = select([
                store_collection_table.c.collection_id,
                store_collection_table.c.store_id,
                store_collection_table.c.catalog_id,
                store_collection_table.c.reference,
                store_collection_table.c.display_name,
                store_collection_table.c.disabled,
            ]) \
                .select_from(store_collection_table) \
                .where(store_collection_table.c.store_id == store_id) \
                .where(store_collection_table.c.catalog_id == catalog_id)

            collections = self._conn.execute(collection_query).all()
            return paginate_response_factory(
                current_page=current_page,
                page_size=dto.page_size,
                total_items=collection_count,
                items=[
                    _row_to_collection_dto(row) for row in collections
                ]
            )
        except Exception as exc:
            raise exc


class SqlFetchAllStoreProductsQuery(FetchAllStoreProductsQuery, SqlQuery):
    def query(
            self,
            collection_reference: StoreCollectionReference,
            catalog_reference: StoreCatalogReference,
            dto: AuthorizedPaginationInputDto
    ) -> PaginationOutputDto[StoreProductResponseDto]:
        try:
            current_page = dto.page if dto.page else 1

            store_id = sql_fetch_store_by_owner(store_owner=dto.current_user, conn=self._conn)
            catalog_id = sql_fetch_catalog_by_reference(catalog_reference=catalog_reference, store_id=store_id,
                                                        conn=self._conn)
            return None
        except Exception as exc:
            raise exc
