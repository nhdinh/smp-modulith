#!/usr/bin/env python
# -*- coding: utf-8 -*-

import injector
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker

from foundation.events import EventBus
from product_catalog import CatalogUnitOfWork, SqlAlchemyCatalogRepository
from product_catalog.application.queries.product_catalog import GetAllCatalogsQuery, GetCatalogQuery
from product_catalog.application.queries.product_catalog import GetAllProductsQuery
from product_catalog_infrastructure.adapter import catalog_db
from product_catalog_infrastructure.adapter.catalog_db import product_table, catalog_table
from product_catalog_infrastructure.queries.product_catalog import SqlGetAllCatalogsQuery, SqlGetCatalogQuery
from product_catalog_infrastructure.queries.product_catalog import SqlGetAllProductsQuery


class ProductCatalogInfrastructureModule(injector.Module):
    @injector.provider
    def catalog_db(self) -> catalog_db:
        return catalog_db

    @injector.provider
    def get_catalog_repo(self, conn: Connection, eventbus: EventBus) -> SqlAlchemyCatalogRepository:
        return SqlAlchemyCatalogRepository(conn, eventbus)

    @injector.provider
    def get_uow(self, conn: Connection) -> CatalogUnitOfWork:
        sessfactory = sessionmaker(bind=conn)
        return CatalogUnitOfWork(sessionfactory=sessfactory)

    @injector.provider
    def get_all_products(self, conn: Connection) -> GetAllProductsQuery:
        return SqlGetAllProductsQuery(conn)

    @injector.provider
    def get_all_catalogs(self, conn: Connection) -> GetAllCatalogsQuery:
        return SqlGetAllCatalogsQuery(conn)

    @injector.provider
    def get_catalog(self, conn: Connection) -> GetCatalogQuery:
        return SqlGetCatalogQuery(conn)


__all__ = [
    # module
    ProductCatalogInfrastructureModule,
    # db_table for creating
    catalog_table, product_table
]
