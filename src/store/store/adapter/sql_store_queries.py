#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import select
from sqlalchemy.engine.row import RowProxy

from db_infrastructure import SqlQuery
from store.adapter.store_db import store_settings_table, store_table, store_owner_table
from store.application.queries.store_queries import FetchStoreProductsFromCollectionQuery, StoreProductResponseDto
from store.application.store_queries import FetchStoreSettingsQuery, StoreSettingResponseDto, \
    CountStoreOwnerByEmailQuery, StoreInfoResponseDto
from store.domain.entities.value_objects import StoreCollectionReference, StoreCatalogReference
from web_app.serialization.dto import PaginationOutputDto, AuthorizedPaginationInputDto


def _row_to_store_settings_dto(row: RowProxy) -> StoreSettingResponseDto:
    return StoreSettingResponseDto(
        name=row.setting_key,
        value=row.setting_value,
        type=row.setting_type,
    )


def _row_to_store_info_dto(store_row_proxy: RowProxy) -> StoreInfoResponseDto:
    return StoreInfoResponseDto(
        store_id=store_row_proxy.store_id,
        store_name=store_row_proxy.name,
        settings=[]
    )


class SqlFetchStoreSettingsQuery(FetchStoreSettingsQuery, SqlQuery):
    def query(self, store_of: str) -> StoreInfoResponseDto:
        store_query = select([
            store_table.c.store_id,
            store_table.c.name,
        ]) \
            .select_from(store_table.join(store_owner_table, onclause=(store_table.c.owner == store_owner_table.c.id))) \
            .select_from(store_table) \
            .where(store_owner_table.c.email == store_of)

        store_row_proxy = self._conn.execute(store_query).first()
        if not store_row_proxy:
            return None

        # make StoreInfoResponseDto
        return_dto = _row_to_store_info_dto(store_row_proxy)

        query = select([
            store_settings_table.c.setting_key,
            store_settings_table.c.setting_value,
            store_settings_table.c.setting_type,
        ]) \
            .select_from(store_settings_table) \
            .where(store_settings_table.c.store_id == return_dto.store_id)

        rows = self._conn.execute(query).all()

        # build settings[]
        for row in rows:
            return_dto.settings.append(_row_to_store_settings_dto(row))

        # return the dto
        return return_dto


class SqlCountStoreOwnerByEmailQuery(CountStoreOwnerByEmailQuery, SqlQuery):
    def query(self, email: str) -> int:
        raise NotImplementedError


class SqlFetchStoreProductsFromCollectionQuery(FetchStoreProductsFromCollectionQuery, SqlQuery):
    def query(self,
              collection_reference: StoreCollectionReference,
              catalog_reference: StoreCatalogReference,
              dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreProductResponseDto]:
        pass
