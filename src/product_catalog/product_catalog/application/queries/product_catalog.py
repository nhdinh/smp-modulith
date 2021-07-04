#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from web_app.serialization.dto import PaginationOutputDto


@dataclass
class CollectionDto:
    collection_reference: str
    collection_display_name: str
    collection_default: bool


@dataclass
class BrandDto:
    brand_reference: str
    brand_display_name: str
    brand_logo: str


@dataclass
class CatalogDto:
    reference: str
    display_name: str
    disabled: bool
    collections: List[CollectionDto]
    system: bool


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


class ListCatalogsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, select_active_only: bool = True) -> List[CatalogDto]:
        pass


class GetCatalogQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, param: str) -> Optional[CatalogDto]:
        pass


class ListProductsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, page: int, page_size: int) -> PaginationOutputDto[ProductDto]:
        pass


class GetProductQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, product_query: str) -> Optional[ProductDto]:
        pass


class ListProductBrandsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self) -> List[BrandDto]:
        pass
