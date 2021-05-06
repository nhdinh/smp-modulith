#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from product_catalog.application.repositories.catalog_repository import SqlAlchemyCatalogRepository
from product_catalog.application.services.catalog_unit_of_work import CatalogUnitOfWork
from product_catalog.application.uc.begin_catalog import BeginningCatalog, BeginningCatalogRequest
from product_catalog.application.uc.create_catalog import CreateCatalog, CreatingCatalogResponseBoundary
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
    'BeginningCatalog',
    # input request dto
    'BeginningCatalogRequest',
    # output request dto
]


class ProductCatalogModule(injector.Module):
    @injector.provider
    def create_catalog_uc(self, boundary: CreatingCatalogResponseBoundary, uow: CatalogUnitOfWork) -> CreateCatalog:
        return CreateCatalog(boundary, uow)

    @injector.provider
    def beginning_catalog_uc(self, uow: CatalogUnitOfWork) -> BeginningCatalog:
        return BeginningCatalog(catalog_uow=uow)
