#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from uuid import UUID

from product_catalog.application.services.catalog_unit_of_work import CatalogUnitOfWork
from product_catalog.domain.entities.catalog import Catalog
from product_catalog.domain.value_objects import CatalogReference


@dataclass
class TestSampleCatalog:
    id: UUID
    reference: CatalogReference
    display_name: str
    disabled: bool = False


class MakeTestSampleCatalogUC:
    def __init__(self, catalog_uow: CatalogUnitOfWork) -> None:
        self.uow = catalog_uow  # type:CatalogUnitOfWork

    def execute(self, request_dto: TestSampleCatalog) -> None:
        with self.uow as uow:
            try:
                catalog = Catalog.create(
                    id=request_dto.id,
                    reference=request_dto.reference,
                    display_name=request_dto.display_name,
                )

                uow.session.add(catalog)
                uow.commit()
            except Exception as exc:
                raise exc
