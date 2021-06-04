#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import select, func, text
from sqlalchemy.engine import Connection

from store.adapter import store_db


class UserCounters:
    def __init__(self, conn: Connection):
        self._conn = conn

    def count(self, email: str):
        return self._conn.scalar(
            select([func.count()]).select_from(store_db.store_owner_table).where(
                store_db.store_owner_table.c.email == email)
        )
