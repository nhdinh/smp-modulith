#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from product_catalog.application.services.catalog_unit_of_work import CatalogUnitOfWork
from product_catalog.domain.entities.catalog import Catalog
from product_catalog.domain.value_objects import CatalogReference


@dataclass
class TestSampleCatalog:
    reference: CatalogReference
    display_name: str
    disabled: bool = False


@dataclass
class DefaultCatalog:
    reference: CatalogReference = 'default_catalog'
    display_name: str = 'Default Catalog'
    disabled: bool = False
    default_collection: str = 'Default collection'


class MakeTestSampleCatalogUC:
    def __init__(self, catalog_uow: CatalogUnitOfWork) -> None:
        self.uow = catalog_uow  # type:CatalogUnitOfWork

    def execute(self, request_dto: TestSampleCatalog) -> None:
        with self.uow as uow:  # type:CatalogUnitOfWork
            try:
                catalog = Catalog.create(
                    reference=request_dto.reference,
                    display_name=request_dto.display_name,
                )

                uow.catalogs.save(catalog)
                uow.commit()
            except Exception as exc:
                raise exc


class MakeDefaultCatalogUC:
    def __init__(self, catalog_uow: CatalogUnitOfWork) -> None:
        self.uow = catalog_uow  # type:CatalogUnitOfWork

    def execute(self, request_dto: DefaultCatalog) -> None:
        with self.uow as uow:  # type:CatalogUnitOfWork
            try:
                default_catalog = uow.catalogs.get_default_catalog()
                if not default_catalog:
                    catalog = Catalog.create(
                        reference=request_dto.reference,
                        display_name=request_dto.display_name,
                        default_collection=request_dto.default_collection
                    )

                    uow.catalogs.save(catalog)
                    uow.commit()
            except Exception as exc:
                raise exc
