#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import select, func
from sqlalchemy.engine import Connection


class UserCounters:
    def __init__(self, conn: Connection):
        self._conn = conn

    def count(self, email: str):
        from store.adapter import store_db

        return self._conn.scalar(
            select([func.count()]).select_from(store_db.store_owner_table).where(
                store_db.store_owner_table.c.email == email)
        )
