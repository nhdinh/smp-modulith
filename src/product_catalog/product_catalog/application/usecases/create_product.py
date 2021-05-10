#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from slugify import slugify

from product_catalog import CatalogUnitOfWork
from product_catalog.domain.entities.catalog import Catalog
from product_catalog.domain.entities.product import Product
from product_catalog.domain.value_objects import ProductReference, CatalogReference


@dataclass
class CreatingProductRequest:
    display_name: str
    reference: Optional[ProductReference] = None
    catalog_reference: Optional[CatalogReference] = None


@dataclass
class CreatingProductResponse:
    product_id: str
    reference: str


class CreatingProductResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: CreatingProductResponse) -> None:
        raise NotImplementedError


class CreateProductUC:
    def __init__(self,
                 output_boundary: CreatingProductResponseBoundary,
                 uow: CatalogUnitOfWork) -> None:
        self._ob = output_boundary
        self._uow = uow

    def execute(self, product_dto: CreatingProductRequest):
        with self._uow as uow:
            try:
                catalog_reference = product_dto.catalog_reference
                product_reference = product_dto.reference
                display_name = product_dto.display_name

                # get default catalog_reference
                if not catalog_reference:
                    catalog = uow.catalogs.get_default_catalog()  # type:Catalog
                else:
                    catalog = uow.catalogs.get(refernce=catalog_reference)

                if not catalog.default_collection:
                    catalog.create_default_collection()

                # make product_reference
                if not product_reference:
                    product_reference = slugify(display_name)

                product = catalog.create_product(
                    reference=product_reference,
                    display_name=display_name
                )  # type:Product

                # output dto
                output_dto = CreatingProductResponse(product_id=str(product.product_id), reference=product.reference)
                self._ob.present(output_dto)

                uow.commit()
            except Exception as exc:
                raise exc
