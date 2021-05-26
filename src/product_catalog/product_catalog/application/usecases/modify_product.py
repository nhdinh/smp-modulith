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
            try:
                product_reference = product_dto.reference
                if product_reference:
                    product = uow.catalogs.find_product(reference=product_reference)

                if not product_reference or not product:
                    raise Exception("Product not found")

                pu = ProductUnit(
                    unit='Cai',
                    default=True
                )

                pu2 = ProductUnit(
                    unit="Thung",
                    base_unit=pu.unit,
                    multiplier=10
                )

                if product_dto.display_name:
                    product.display_name = product_dto.display_name

                product.units.add(pu)
                uow.commit()

                product.units.add(pu2)

                output_dto = ModifyingProductResponse(product_id=str(product.product_id), reference=product_reference)
                self._ob.present(output_dto)

                uow.commit()
            except Exception as exc:
                raise exc

    def modify_product_info(
            self,
            product: Product,
            display_name: str):
        pass

    def modify_product_catalog_or_collection(
            self,
            product: Product,
            **kwargs
    ):
        pass
