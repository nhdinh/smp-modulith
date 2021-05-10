#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from product_catalog.application.repositories.catalog_repository import SqlAlchemyCatalogRepository
from product_catalog.application.services.catalog_unit_of_work import CatalogUnitOfWork
from product_catalog.application.usecases.begin_catalog import MakeTestSampleCatalogUC, TestSampleCatalog, \
    MakeDefaultCatalogUC
from product_catalog.application.usecases.create_catalog import CreateCatalogUC, CreatingCatalogResponseBoundary, \
    CreateDefaultCatalogUC
from product_catalog.application.usecases.create_product import CreatingProductResponseBoundary, CreateProductUC
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
    def create_product_uc(self, boundary: CreatingProductResponseBoundary, uow: CatalogUnitOfWork) -> CreateProductUC:
        return CreateProductUC(boundary, uow)

    @injector.provider
    def beginning_catalog_uc(self, uow: CatalogUnitOfWork) -> MakeTestSampleCatalogUC:
        return MakeTestSampleCatalogUC(catalog_uow=uow)

    @injector.provider
    def make_default_catalog_uc(self, uow: CatalogUnitOfWork) -> MakeDefaultCatalogUC:
        return MakeDefaultCatalogUC(catalog_uow=uow)
