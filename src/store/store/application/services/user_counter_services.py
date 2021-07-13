#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import select, func
from sqlalchemy.engine import Connection


class UserCounters:
    def __init__(self, conn: Connection):
        self._conn = conn

    def count(self, email: str):
        from store.adapter import shop_db

        return self._conn.scalar(
            select([func.count()]).select_from(shop_db.shop_user_table).where(
                shop_db.shop_user_table.c.email == email)
        )
