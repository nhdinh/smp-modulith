#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from typing import List, Optional, Tuple


@dataclass
class PaginationDto:
    data: List
    current_page: int
    page_size: int
    total_rows: int
    total_pages: int


@dataclass
class CatalogDto:
    reference: str
    display_name: str
    disabled: bool


@dataclass
class ProductDto:
    reference: str
    display_name: str
    catalog: str
    collection: str

    # TODO: Add more field to ProductDto base on what to display at frontend
    def serialize(self):
        return {
            'reference': self.reference,
            'display_name': self.display_name,
            'catalog': self.catalog,
            'collection': self.collection
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
