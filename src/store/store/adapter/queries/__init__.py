#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db_infrastructure import SqlQuery
from store.application.queries.store_queries import FetchAllStoreCatalogsQuery
from web_app.serialization.dto import PaginationOutputDto


class SqlFetchAllStoreCatalogsQuery(FetchAllStoreCatalogsQuery, SqlQuery):
    def query(self) -> PaginationOutputDto:
        pass
