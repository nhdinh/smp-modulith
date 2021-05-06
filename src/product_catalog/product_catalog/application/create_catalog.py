#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID

from product_catalog.domain.entities.catalog import Catalog
from product_catalog_infrastructure.services.catalog_unit_of_work import CatalogUnitOfWork


@dataclass
class CreateCatalogInputDto:
    reference: str
    display_name: str
    default_collection: Optional[str]
    collections: Optional[List[str]]


@dataclass
class CreatingCatalogResponse:
    id: UUID
    reference: str


class CreatingCatalogOutputBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, output_dto: CreatingCatalogResponse) -> None:
        raise NotImplementedError


class CreateCatalog:
    def __init__(self,
                 output_boundary: CreatingCatalogOutputBoundary,
                 uow: CatalogUnitOfWork) -> None:
        self._output_boundary = output_boundary
        self._uow = uow

    def execute(self, input_dto: CreateCatalogInputDto) -> None:
        with self._uow as uow:
            try:
                search_for_catalog = uow.session.query(Catalog).filter(Catalog.reference == input_dto.reference).count()
                if search_for_catalog:
                    raise Exception("Catalog has been existed")

                catalog = Catalog(
                    reference=input_dto.reference,
                    display_name=input_dto.display_name
                )
                uow.session.add(catalog)
                uow.commit()
            except Exception as exc:
                raise exc
