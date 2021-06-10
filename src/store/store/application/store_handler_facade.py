#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.engine import Connection


class StoreHandlerFacade:
    def __init__(self, connection: Connection):
        self._conn = connection
