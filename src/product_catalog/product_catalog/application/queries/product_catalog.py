#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import datetime

from typing import List, Optional
from uuid import UUID


@dataclass
class PaginationDto:
    items: List
    current_page: int
    page_size: int
    total_items: int
    total_pages: int


@dataclass
class CatalogDto:
    reference: str
    display_name: str
    disabled: bool


@dataclass
class ProductDto:
    product_id: UUID
    reference: str
    display_name: str
    catalog: str
    collection: str
    brand: str
    created_at: datetime

    # TODO: Add more field to ProductDto base on what to display at frontend
    def serialize(self):
        return {
            'product_id': self.product_id,
            'reference': self.reference,
            'display_name': self.display_name,
            'catalog': self.catalog,
            'collection': self.collection,
            'brand': self.brand,
            'created_at': self.created_at,
        }


class GetAllCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, page: int, page_size: int) -> PaginationDto:
        pass


class GetCatalogQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, param: str) -> Optional[CatalogDto]:
        pass


class GetCatalogByReferenceQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, reference: str) -> CatalogDto:
        pass


class GetAllProductsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, page: int, page_size: int) -> PaginationDto:
        pass
