#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from product_catalog import CatalogReference, CatalogUnitOfWork, CollectionReference


@dataclass
class CreatingCollectionRequest:
    reference: CollectionReference
    display_name: str
    catalog_reference: CatalogReference


@dataclass
class CreatingCollectionResponse:
    reference: str


class CreatingCollectionResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: CreatingCollectionResponse) -> None:
        raise NotImplementedError


class CreateCollectionUC:
    def __init__(self,
                 output_boundary: CreatingCollectionResponseBoundary,
                 uow: CatalogUnitOfWork) -> None:
        self._ob = output_boundary
        self._uow = uow

    def execute(self, input_dto: CreatingCollectionRequest) -> None:
        pass
