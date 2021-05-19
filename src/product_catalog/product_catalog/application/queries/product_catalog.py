#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from typing import List, Optional, Tuple


@dataclass
class PaginationDto:
    current_page: int
    page_size: int
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


class GetAllCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, page: int, page_size: int) -> Tuple[List[CatalogDto], PaginationDto]:
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
    def query(self, page: int, page_size: int) -> Tuple[List[ProductDto], PaginationDto]:
        pass
