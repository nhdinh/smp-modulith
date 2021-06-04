#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.engine.row import RowProxy
from typing import List

from db_infrastructure import SqlQuery
from identity.adapters.identity_db import user_table
from store.adapter.store_db import store_settings_table, store_table

from store.application.store_queries import FetchStoreSettingsQuery, StoreSettingsDto, CountStoreOwnerByEmailQuery


def _row_to_store_settings_dto(row: RowProxy) -> StoreSettingsDto:
    return StoreSettingsDto(
        name=row.setting_name,
        value=row.setting_value,
        type=row.setting_type,
    )


class SqlFetchStoreSettingsQuery(FetchStoreSettingsQuery, SqlQuery):
    def query(self, store_of: str) -> List[StoreSettingsDto]:
        joined_table = store_settings_table \
            .join(store_table, onclause=(store_settings_table.c.store_id == store_table.c.store_id)) \
            .join(user_table, onclause=(store_table.c.owner == user_table.c.id))

        query = select([
            store_settings_table.c.setting_name,
            store_settings_table.c.setting_value,
            store_settings_table.c.setting_type,
        ]) \
            .select_from(joined_table) \
            .select_from(store_settings_table) \
            .select_from(user_table) \
            .where(user_table.c.email == store_of)

        rows = self._conn.execute(query)
        return [
            _row_to_store_settings_dto(row) for row in rows
        ]


class SqlCountStoreOwnerByEmailQuery(CountStoreOwnerByEmailQuery, SqlQuery):
    def query(self, email: str) -> int:
        raise NotImplementedError
