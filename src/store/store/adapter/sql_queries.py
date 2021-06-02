#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uuid import UUID

from sqlalchemy.engine.row import RowProxy
from store.adapter.store_db import store_settings_table

from auctions_infrastructure.queries.base import SqlQuery
from store.application.store_queries import FetchStoreSettingsQuery, StoreSettingsDto


def _row_to_store_settings_dto(row: RowProxy) -> StoreSettingsDto:
    return StoreSettingsDto(
        name=row.name,
        value=row.value,
    )


class SqlFetchStoreSettingsQuery(FetchStoreSettingsQuery, SqlQuery):
    def query(self, store_id: UUID) -> StoreSettingsDto:
        row = self._conn.execute(store_settings_table.select().where(store_settings_table.store_id == store_id))
        return _row_to_store_settings_dto(row)
