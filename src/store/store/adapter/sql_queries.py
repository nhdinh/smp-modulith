#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uuid import UUID

from sqlalchemy.engine.row import RowProxy

from identity.adapters.identity_db import user_table
from store.adapter.store_db import store_settings_table, store_table

from auctions_infrastructure.queries.base import SqlQuery
from store.application.store_queries import FetchStoreSettingsQuery, StoreSettingsDto


def _row_to_store_settings_dto(row: RowProxy) -> StoreSettingsDto:
    return StoreSettingsDto(
        name=row.name,
        value=row.value,
    )


class SqlFetchStoreSettingsQuery(FetchStoreSettingsQuery, SqlQuery):
    def query(self, store_of: str) -> StoreSettingsDto:
        joined_table = store_settings_table \
            .join(store_table, onclause=(store_settings_table.c.store_id == store_table.c.store_id)) \
            .join(user_table, onclause=(store_table.c.owner == user_table.c.id))

        query = 'something'

        row = self._conn.execute(store_settings_table.select().where(store_settings_table.store_id == store_id))
        return _row_to_store_settings_dto(row)
