#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import select, func
from sqlalchemy.engine import Connection

from shop.adapter.shop_db import shop_users_table


class ShopUserCounter:
    def __init__(self, connection: Connection):
        self._conn = connection

    def is_shop_user_email_existed(self, email: str):
        email = email.strip()
        sql = select(func.count(shop_users_table.c.email)).where(func.lower(shop_users_table.c.email) == email.lower())
        return self._conn.scalar(sql)

    def is_shop_user_phone_existed(self, phone: str):
        phone = phone.strip()
        sql = select(func.count(shop_users_table.c.email)).where(func.lower(shop_users_table.c.mobile) == phone.lower())
        return self._conn.scalar(sql)
