#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID

from flask import Response

from product_catalog.domain.entities.catalog import Catalog
from product_catalog.application.services.catalog_unit_of_work import CatalogUnitOfWork


@dataclass
class CreatingCatalogRequest:
    reference: str
    display_name: str
    default_collection: Optional[str] = None
    collections: Optional[List[str]] = None


@dataclass
class CreatingCatalogResponse:
    id: str
    reference: str


class CreatingCatalogResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: CreatingCatalogResponse) -> None:
        raise NotImplementedError


class CreateCatalogUC:
    def __init__(self,
                 output_boundary: CreatingCatalogResponseBoundary,
                 uow: CatalogUnitOfWork) -> None:
        self._output_boundary = output_boundary
        self._uow = uow

    def execute(self, input_dto: CreatingCatalogRequest) -> None:
        with self._uow as uow:
            try:
                search_for_catalog = uow.session.query(Catalog).filter(Catalog.reference == input_dto.reference).count()
                if search_for_catalog:
                    raise Exception("Catalog has been existed")

                catalog = Catalog.create(
                    reference=input_dto.reference,
                    display_name=input_dto.display_name
                )
                uow.session.add(catalog)

                # output dto
                output_dto = CreatingCatalogResponse(id=str(catalog.id), reference=catalog.reference)
                self._output_boundary.present(output_dto)

                uow.commit()
            except Exception as exc:
                raise exc
