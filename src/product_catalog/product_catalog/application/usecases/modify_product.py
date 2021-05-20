#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from product_catalog.domain.value_objects import ProductReference, CollectionReference, CatalogReference


@dataclass
class ModifyingProductRequest:
    display_name: str
    reference: Optional[ProductReference] = None
    catalog_reference: Optional[CatalogReference] = None
    collection_reference: Optional[CollectionReference] = None


@dataclass
class ModifyingProductResponse:
    product_id: str
    reference: str


class ModifyingProductResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: ModifyingProductResponse) -> None:
        raise NotImplementedError


class ModifyProductUC:
    def __init__(self):
        pass

    def execute(self, product_dto: ModifyingProductRequest):
        raise NotImplementedError
