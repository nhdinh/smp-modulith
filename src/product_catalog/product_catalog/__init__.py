#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker

from product_catalog.adapter import catalog_db
from product_catalog.adapter.catalog_db import catalog_table, product_table
from product_catalog.adapter.queries.product_catalog import SqlFetchCatalogQuery, SqlFetchAllCatalogsQuery, \
    SqlFetchAllProductsQuery, SqlFetchProductQuery, SqlFetchAllBrandsQuery
from product_catalog.application.queries.product_catalog import FetchAllProductsQuery, FetchAllCatalogsQuery, \
    FetchCatalogQuery, FetchProductQuery, FetchAllBrandsQuery
from product_catalog.application.repositories.catalog_repository import SqlAlchemyCatalogRepository
from product_catalog.application.services.catalog_unit_of_work import CatalogUnitOfWork
from product_catalog.application.usecases.begin_catalog import MakeTestSampleCatalogUC, TestSampleCatalog, \
    MakeDefaultCatalogUC
from product_catalog.application.usecases.create_catalog import CreateCatalogUC, CreatingCatalogResponseBoundary, \
    CreateDefaultCatalogUC
from product_catalog.application.usecases.create_product import CreatingProductResponseBoundary, CreateProductUC
from product_catalog.application.usecases.delete_catalog import DeletingCatalogResponseBoundary, DeleteCatalogUC
from product_catalog.application.usecases.modify_product import ModifyingProductResponseBoundary, ModifyProductUC
from product_catalog.application.usecases.toggle_catalog import TogglingCatalogResponseBoundary, ToggleCatalogUC
from product_catalog.domain.value_objects import CollectionReference, CatalogId, CatalogReference

__all__ = [
    # module
    'ProductCatalogModule',
    # value objects
    'CatalogId', 'CatalogReference', 'CollectionReference',
    # repositories
    'SqlAlchemyCatalogRepository',
    # unit of work
    'CatalogUnitOfWork',
    # usecase(s)
    'MakeTestSampleCatalogUC',
    # input request dto
    'TestSampleCatalog',
    # output request dto
    # module
    'ProductCatalogInfrastructureModule',
    # db_table for creating
    'catalog_table', 'product_table'
]


class ProductCatalogModule(injector.Module):
    @injector.provider
    def create_catalog_uc(self, boundary: CreatingCatalogResponseBoundary, uow: CatalogUnitOfWork) -> CreateCatalogUC:
        return CreateCatalogUC(boundary, uow)

    @injector.provider
    def create_default_catalog_uc(self, boundary: CreatingCatalogResponseBoundary,
                                  uow: CatalogUnitOfWork) -> CreateDefaultCatalogUC:
        return CreateDefaultCatalogUC(boundary, uow)

    @injector.provider
    def beginning_catalog_uc(self, uow: CatalogUnitOfWork) -> MakeTestSampleCatalogUC:
        return MakeTestSampleCatalogUC(catalog_uow=uow)

    @injector.provider
    def make_default_catalog_uc(self, uow: CatalogUnitOfWork) -> MakeDefaultCatalogUC:
        return MakeDefaultCatalogUC(catalog_uow=uow)

    @injector.provider
    def create_product_uc(self, boundary: CreatingProductResponseBoundary, uow: CatalogUnitOfWork) -> CreateProductUC:
        return CreateProductUC(boundary, uow)

    @injector.provider
    def modify_product_uc(self, boundary: ModifyingProductResponseBoundary, uow: CatalogUnitOfWork) -> ModifyProductUC:
        return ModifyProductUC(boundary, uow)

    @injector.provider
    def toggle_catalog_uc(self, boundary: TogglingCatalogResponseBoundary, uow: CatalogUnitOfWork) -> ToggleCatalogUC:
        return ToggleCatalogUC(boundary, uow)

    @injector.provider
    def delete_catalog_uc(self, boundary: DeletingCatalogResponseBoundary, uow: CatalogUnitOfWork) -> DeleteCatalogUC:
        return DeleteCatalogUC(boundary, uow)


class ProductCatalogInfrastructureModule(injector.Module):
    @injector.provider
    def catalog_db(self) -> catalog_db:
        return catalog_db

    @injector.provider
    def get_uow(self, conn: Connection) -> CatalogUnitOfWork:
        sessfactory = sessionmaker(bind=conn)
        return CatalogUnitOfWork(sessionfactory=sessfactory)

    @injector.provider
    def get_all_products_query(self, conn: Connection) -> FetchAllProductsQuery:
        return SqlFetchAllProductsQuery(conn)

    @injector.provider
    def get_all_catalogs_query(self, conn: Connection) -> FetchAllCatalogsQuery:
        return SqlFetchAllCatalogsQuery(conn)

    @injector.provider
    def get_catalog_query(self, conn: Connection) -> FetchCatalogQuery:
        return SqlFetchCatalogQuery(conn)

    @injector.provider
    def get_product_query(self, conn: Connection) -> FetchProductQuery:
        return SqlFetchProductQuery(conn)

    @injector.provider
    def fetch_all_brands(self, conn: Connection) -> FetchAllBrandsQuery:
        return SqlFetchAllBrandsQuery(conn)
