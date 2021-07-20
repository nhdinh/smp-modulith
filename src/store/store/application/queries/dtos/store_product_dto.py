#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import List, Union

from sqlalchemy.engine.row import RowProxy

from db_infrastructure import GUID
from store.application.queries.dtos.store_catalog_dto import (
    StoreCatalogResponseCompactedDto,
    StoreCatalogResponseDto,
    _row_to_catalog_dto,
)
from store.application.queries.dtos.store_collection_dto import StoreCollectionDto, _row_to_collection_dto
from store.application.queries.dtos.store_product_brand_dto import (
    StoreProductBrandCompactedDto,
    StoreProductBrandDto,
    _row_to_brand_dto,
)
from store.application.queries.dtos.store_product_tag_dto import StoreProductTagDto, _row_to_tag_dto
from store.application.queries.dtos.store_product_unit_dto import StoreProductUnitDto, _row_to_unit_dto
from store.application.queries.dtos.store_supplier_dto import StoreSupplierDto, _row_to_supplier_dto


@dataclass
class StoreProductCompactedDto:
    product_id: GUID
    title: str
    sku: str
    image: str

    brand: StoreProductBrandCompactedDto
    catalog: StoreCatalogResponseCompactedDto

    collections: List[StoreCollectionDto]
    suppliers: List[StoreSupplierDto]

    def serialize(self):
        return self.__dict__


@dataclass
class StoreProductDto(StoreProductCompactedDto):
    # barcode: str
    restock_threshold: int
    max_stock_threshold: int

    # created_at: datetime
    # updated_at: datetime

    brand: StoreProductBrandDto
    catalog: StoreCatalogResponseDto

    # default_unit: StoreProductUnitDto

    units: List[StoreProductUnitDto]
    tags: List[StoreProductTagDto]
    collections: List[StoreCollectionDto]


def _row_to_product_dto(
        row: RowProxy,
        unit_rows: List[RowProxy] = None,
        tag_rows: List[RowProxy] = None,
        collection_rows: List[RowProxy] = None,
        supplier_rows: List[RowProxy] = None,
        compacted=True
) -> Union[StoreProductCompactedDto, StoreProductDto]:
    if hasattr(row, 'product_cache_id'):  # use cache
        product_data = {
            'product_id': row.product_cache_id,
            'title': row.title,
            'sku': row.sku,
            'image': row.image,

            'brand': row.brand_json,
            'catalog': row.catalog_json,
            'suppliers': row.suppliers_json,
            'collections': row.collections_json,
        }
    else:  # query from data
        product_data = {
            'product_id': row.product_id,
            'title': row.title,
            'sku': row.sku,
            'image': row.image,

            'brand': _row_to_brand_dto(row=row) if row.brand_id else None,
            'catalog': _row_to_catalog_dto(row=row, collections=[]) if row.catalog_id else None,
            'suppliers': [_row_to_supplier_dto(row=supplier_row) for supplier_row in
                          supplier_rows] if supplier_rows else [],
            'collections': [_row_to_collection_dto(collection_row) for collection_row in
                            collection_rows] if collection_rows else []
        }

    if compacted:
        return StoreProductCompactedDto(**product_data)
    else:
        full_product_data = {
            'brand': _row_to_brand_dto(row=row, compacted=False),
            'catalog': _row_to_catalog_dto(row=row, collections=[], compacted=False),
            # 'barcode': row.barcode,
            'restock_threshold': row.restock_threshold,
            'max_stock_threshold': row.max_stock_threshold,

            # 'default_unit': row.default_unit,
            'units': [_row_to_unit_dto(unit_row) for unit_row in unit_rows] if unit_rows else [],
            'tags': [_row_to_tag_dto(tag_row) for tag_row in tag_rows] if tag_rows else [],
        }
        product_data.update(full_product_data)
        return StoreProductDto(**product_data)
