#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime

from shop.domain.entities.value_objects import ShopCatalogId


@dataclass
class ShopCatalogShortDto:
    catalog_id: ShopCatalogId
    catalog_title: str
    catalog_image: str
    is_default_catalog: bool

    def serialize(self):
        return self.__dict__


@dataclass
class ShopCatalogDto(ShopCatalogShortDto):
    is_default_catalog: bool
    product_count: int
    collection_count: int
    created_at: datetime
    updated_at: datetime
    status: str

    # collections: List[ShopCollectionDto]
