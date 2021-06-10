#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.engine import Connection


class SqlQuery:
    def __init__(self, connection: Connection) -> None:
        self._conn = connection


def paginate(query, page: int, page_size: int):
    return query.limit(page_size).offset(page_size * (page - 1))
