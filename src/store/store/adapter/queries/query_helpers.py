#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List

from sqlalchemy.engine.row import RowProxy

from store.application.queries.store_queries import StoreCatalogResponseDto, StoreCollectionResponseDto, \
    StoreProductShortResponseDto, StoreProductResponseDto, StoreProductUnitResponseDto, StoreProductTagResponseDto
from store.application.store_queries import StoreSettingResponseDto, StoreInfoResponseDto


def _row_to_catalog_dto(row: RowProxy, collections: List[RowProxy]) -> StoreCatalogResponseDto:
    return StoreCatalogResponseDto(
        catalog_id=row.catalog_id,
        store_id=row.store_id,
        reference=row.reference,
        title=row.title,
        default=row.default,
        disabled=row.disabled,
        collections=[
            _row_to_collection_dto(collection_row) for collection_row in collections
        ],
    )


def _row_to_collection_dto(row: RowProxy) -> StoreCollectionResponseDto:
    return StoreCollectionResponseDto(
        collection_id=row.collection_id,
        reference=row.reference,
        title=row.title,
        disabled=row.disabled,
        default=row.default,
    )


def _row_to_product_short_dto(product_proxy: RowProxy) -> StoreProductShortResponseDto:
    return StoreProductShortResponseDto(
        product_id=product_proxy.product_id,
        reference=product_proxy.reference,
        display_name=product_proxy.display_name,
        image=product_proxy.image,
        catalog=product_proxy.catalog_display_name,
        brand=product_proxy.brand_display_name,
        collection=product_proxy.collection_display_name,
        created_at=product_proxy.created_at,
    )


def _row_to_store_settings_dto(row: RowProxy) -> StoreSettingResponseDto:
    return StoreSettingResponseDto(
        name=row.setting_key,
        value=row.setting_value,
        type=row.setting_type,
    )


def _row_to_store_info_dto(store_row_proxy: RowProxy) -> StoreInfoResponseDto:
    return StoreInfoResponseDto(
        store_id=store_row_proxy.store_id,
        store_name=store_row_proxy.name,
        settings=[]
    )


def _row_to_unit_dto(row: RowProxy) -> StoreProductUnitResponseDto:
    return StoreProductUnitResponseDto(
        unit=row.unit,
        conversion_factor=row.conversion_factor,
    )


def _row_to_tag_dto(row: RowProxy):
    return row.tag


def _row_to_product_dto(
        product_proxy: RowProxy,
        units: List[StoreProductUnitResponseDto] = None,
        tags: List[StoreProductTagResponseDto] = None,
) -> StoreProductResponseDto:
    return StoreProductResponseDto(
        product_id=product_proxy.product_id,
        reference=product_proxy.reference,
        display_name=product_proxy.display_name,

        brand=product_proxy.brand_display_name,
        catalog=product_proxy.catalog_display_name,
        catalog_reference=product_proxy.catalog_reference,
        collection=product_proxy.collection_display_name,
        collection_reference=product_proxy.collection_reference,
        created_at=product_proxy.created_at,
        updated_at=product_proxy.updated_at,

        units=[_row_to_unit_dto(unit_row) for unit_row in units] if units else [],
        tags=[_row_to_tag_dto(tag_row) for tag_row in tags] if tags else []
    )
