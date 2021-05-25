#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from product_catalog import CatalogUnitOfWork
from product_catalog.domain.entities.product import Product
from product_catalog.domain.entities.product_unit import ProductUnit
from product_catalog.domain.value_objects import ProductReference, CollectionReference, CatalogReference


@dataclass
class ModifyingProductRequest:
    reference: ProductReference
    display_name: Optional[str]
    catalog_reference: Optional[CatalogReference] = None
    catalog_display_name: Optional[str] = None
    collection_reference: Optional[CollectionReference] = None
    collection_display_name: Optional[str] = None
    brand_reference: Optional[str] = None
    brand_display_name: Optional[str] = None


@dataclass
class ModifyingProductResponse:
    product_id: str
    reference: str


class ModifyingProductResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: ModifyingProductResponse) -> None:
        raise NotImplementedError


class ModifyProductUC:
    def __init__(self,
                 output_boundary: ModifyingProductResponseBoundary,
                 uow: CatalogUnitOfWork) -> None:
        self._ob = output_boundary
        self._uow = uow

    def execute(self, product_dto: ModifyingProductRequest):
        with self._uow as uow:
            pass
