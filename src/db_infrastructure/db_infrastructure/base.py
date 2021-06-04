#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.engine import Connection


class SqlQuery:
    def __init__(self, connection: Connection) -> None:
        self._conn = connection
