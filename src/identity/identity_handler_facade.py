#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

from identity.adapters.identity_db import user_table
from sqlalchemy import insert

from identity.domain.value_objects import UserId
from sqlalchemy.engine import Connection


class IdentityHandlerFacade:
    def __init__(self, connection: Connection):
        self._conn = connection  # type:Connection

    def create_user(self, user_id: UserId, email: str, mobile: str, hashed_password: str):
        query = insert(user_table).values(
            id=user_id,
            email=email,
            mobile=mobile,
            password=hashed_password,
            active=True,
            confirmed_at=datetime.now(),
        )

        try:
            self._conn.execute(query)
        except Exception as exc:
            raise exc
