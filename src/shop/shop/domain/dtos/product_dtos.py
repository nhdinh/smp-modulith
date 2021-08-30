#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from dataclasses import dataclass
from datetime import date
from typing import List, Union

from sqlalchemy.engine.row import RowProxy

from foundation.value_objects import Money
from foundation.value_objects.currency import _get_registered_currency_or_default
from shop.domain.dtos.catalog_dtos import ShopCatalogDto
from web_app.serialization.dto import row_proxy_to_dto
from shop.domain.dtos.collection_dtos import ShopCollectionDto, _row_to_collection_dto
from shop.domain.dtos.product_tag_dtos import StoreProductTagDto, _row_to_tag_dto
from shop.domain.dtos.product_unit_dtos import ShopProductUnitDto, _row_to_unit_dto
from shop.domain.dtos.shop_brand_dtos import ShopBrandDto
from shop.domain.dtos.supplier_dtos import ShopSupplierDto, _row_to_supplier_dto
from shop.domain.entities.value_objects import ShopProductId, ShopSupplierId


@dataclass
class ShopProductDto:
    product_id: ShopProductId
    title: str
    sku: str
    description: str
    image: str
    status: str

    brand: ShopBrandDto
    catalog: ShopCatalogDto

    collections: List[ShopCollectionDto]
    suppliers: List[ShopSupplierDto]
    # barcode: str
    restock_threshold: int
    max_stock_threshold: int

    created_at: datetime
    updated_at: datetime

    brand: ShopBrandDto
    catalog: ShopCatalogDto

    # default_unit: StoreProductUnitDto

    units: List[ShopProductUnitDto]
    tags: List[StoreProductTagDto]
    collections: List[ShopCollectionDto]

    def serialize(self):
        return self.__dict__


@dataclass
class ShopProductPriceDto:
    product_id: ShopProductId
    unit_name: str
    supplier_id: ShopSupplierId
    price: Money
    tax: float
    effective_from: date
    effective_status: str

    def serialize(self):
        return self.__dict__


def _row_to_product_dto(
        row: RowProxy,
        unit_rows: List[RowProxy] = None,
        tag_rows: List[RowProxy] = None,
        collection_rows: List[RowProxy] = None,
        supplier_rows: List[RowProxy] = None,
) -> ShopProductDto:
    if hasattr(row, 'product_cache_id'):  # use cache
        product_data = {
            'product_id': row.product_id,
            'title': row.title,
            'sku': row.sku,
            'description': row.description,
            'image': row.image,
            'status': row.status,
            'created_at': row.created_at,
            'updated_at': row.updated_at,

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
            'description': row.description,
            'image': row.image,
            'status': row.status,
            'created_at': row.created_at,
            'updated_at': row.updated_at,

            'brand': row_proxy_to_dto(rows=[row], klass=ShopBrandDto) if row.brand_id else None,
            'catalog': row_proxy_to_dto(rows=[row], klass=ShopCatalogDto) if row.catalog_id else None,
            'suppliers': [_row_to_supplier_dto(row=supplier_row, contact_rows=[]) for supplier_row in
                          supplier_rows] if supplier_rows else [],
            'collections': [_row_to_collection_dto(collection_row) for collection_row in
                            collection_rows] if collection_rows else []
        }

    full_product_data = {
        'brand': row_proxy_to_dto(rows=[row], klass=ShopBrandDto) if row.brand_id else None,
        'catalog': row_proxy_to_dto(row, ShopCatalogDto),
        # 'barcode': row.barcode,
        'restock_threshold': row.restock_threshold,
        'max_stock_threshold': row.max_stock_threshold,

        # 'default_unit': row.default_unit,
        'units': [_row_to_unit_dto(unit_row) for unit_row in unit_rows] if unit_rows else [],
        'tags': [_row_to_tag_dto(tag_row) for tag_row in tag_rows] if tag_rows else [],
    }
    product_data.update(full_product_data)
    return ShopProductDto(**product_data)


def _row_to_product_price_dto(row: RowProxy) -> ShopProductPriceDto:
    return ShopProductPriceDto(
        product_id=row.product_id,
        unit_name=row.unit_name,
        supplier_id=row.supplier_id,
        price=Money(currency=_get_registered_currency_or_default(row.currency), amount=row.price),
        tax=row.tax,
        effective_from=row.effective_from,
        effective_status=''
    )
