#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from product_catalog.application.repositories.catalog_repository import SqlAlchemyCatalogRepository
from product_catalog.application.services.catalog_unit_of_work import CatalogUnitOfWork
from product_catalog.application.uc.begin_catalog import MakeTestSampleCatalogUC, TestSampleCatalog
from product_catalog.application.uc.create_catalog import CreateCatalogUC, CreatingCatalogResponseBoundary
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
    def beginning_catalog_uc(self, uow: CatalogUnitOfWork) -> MakeTestSampleCatalogUC:
        return MakeTestSampleCatalogUC(catalog_uow=uow)
