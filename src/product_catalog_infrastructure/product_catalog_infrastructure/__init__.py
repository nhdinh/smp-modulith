#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    # database table
    'collection_table', 'catalog_table', 'product_table'
]

import injector
from sqlalchemy.engine import Connection

from product_catalog.application.queries.product_catalog import GetAllCatalogsQuery, GetCatalogQuery
from product_catalog_infrastructure.adapter.catalog_db import collection_table, product_table, catalog_table
from product_catalog_infrastructure.queries.product_catalog import SqlGetAllCatalogsQuery, SqlGetCatalogQuery


class ProductCatalogInfrastructure(injector.Module):
    @injector.provider
    def get_all_catalogs(self, conn: Connection) -> GetAllCatalogsQuery:
        return SqlGetAllCatalogsQuery(conn)

    @injector.provider
    def get_catalog(self, conn: Connection) -> GetCatalogQuery:
        return SqlGetCatalogQuery(conn)
