#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List

from sqlalchemy.engine.row import RowProxy

from store.application.queries.response_dtos import StoreCollectionResponseDto, StoreProductShortResponseDto, \
    StoreSettingResponseDto, StoreInfoResponseDto, StoreProductUnitResponseDto, StoreCatalogResponseDto, \
    StoreProductBrandResponseDto, StoreProductTagResponseDto, StoreProductResponseDto, StoreWarehouseResponseDto, \
    StoreAddressResponseDto, StoreSupplierResponseDto, StoreCatalogResponseCompactedDto


def _row_to_collection_dto(row: RowProxy) -> StoreCollectionResponseDto:
    return StoreCollectionResponseDto(
        collection_id=row.collection_id,
        reference=row.reference,
        title=row.title,
        is_collection_disabled=row.is_collection_disabled,
    )


def _row_to_product_short_dto(product_proxy: RowProxy) -> StoreProductShortResponseDto:
    return StoreProductShortResponseDto(
        product_id=product_proxy.product_id,
        reference=product_proxy.reference,
        title=product_proxy.title,
        image=product_proxy.image,
        catalog=product_proxy.catalog_title,
        catalog_id=product_proxy.catalog_id,
        brand=product_proxy.brand_name,
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
        unit_name=row.unit_name,
        default=row.default,
        referenced_unit_name=row.referenced_unit_name,
        conversion_factor=row.conversion_factor,
    )


def _row_to_catalog_dto(row: RowProxy, collections: List[RowProxy]) -> StoreCatalogResponseDto:
    return StoreCatalogResponseDto(
        catalog_id=row.catalog_id,
        store_id=row.store_id,
        reference=row.reference,
        title=row.title,
        is_default_catalog=row.is_default_catalog,
        is_catalog_disabled=row.is_catalog_disabled,
        collections=[
            _row_to_collection_dto(collection_row) for collection_row in collections
        ],
    )


def _row_to_catalog_compacted_dto(row: RowProxy) -> StoreCatalogResponseCompactedDto:
    return StoreCatalogResponseCompactedDto(
        catalog_id=row.catalog_id,
        catalog_reference=row.catalog_reference,
        catalog_title=row.catalog_title,
        catalog_image=row.catalog_image,
        is_catalog_disabled=row.is_catalog_disabled,
    )


def _row_to_tag_dto(row: RowProxy):
    return row.tag


def _row_to_brand_dto(row: RowProxy):
    return StoreProductBrandResponseDto(
        brand_id=row.brand_id,
        brand_name=row.brand_name,
        logo=row.logo,
    )


def _row_to_product_dto(
        product_row: RowProxy,
        unit_rows: List[RowProxy] = None,
        tag_rows: List[RowProxy] = None,
        collection_rows: List[RowProxy] = None,
) -> StoreProductResponseDto:
    return StoreProductResponseDto(
        product_id=product_row.product_id,
        reference=product_row.reference,
        title=product_row.title,

        brand=_row_to_brand_dto(product_row) if product_row.brand_id else None,
        catalog=_row_to_catalog_compacted_dto(product_row),

        # collection=product_proxy.collection_display_name,
        # collection_reference=product_proxy.collection_reference,
        created_at=product_row.created_at,
        updated_at=product_row.updated_at,

        units=[_row_to_unit_dto(unit_row) for unit_row in sorted(unit_rows)] if unit_rows else [],
        tags=[_row_to_tag_dto(tag_row) for tag_row in tag_rows] if tag_rows else [],
        collections=[_row_to_collection_dto(collection_row) for collection_row in
                     collection_rows] if collection_rows else [],
    )


def _row_to_warehouse_dto(row: RowProxy) -> StoreWarehouseResponseDto:
    return StoreWarehouseResponseDto(
        warehouse_id=row.warehouse_id,
        warehouse_name=row.warehouse_name,
        default=row.default,
        disabled=row.disabled,
    )


def _row_to_address_dto(row: RowProxy) -> StoreAddressResponseDto:
    return StoreAddressResponseDto(
        store_address_id=row.store_address_id,
        full_address=f"{row._street_address}, {row._sub_division_name}, {row._division_name}, {row._city_name}, {row._country_name}",
        street_address=row._street_address,
        sub_division_name=row._sub_division_name,
        division_name=row._division_name,
        city_name=row._city_name,
        country_name=row._country_name,
        iso_code=row._iso_code,
        address_type=row.address_type,
        recipient=row.recipient,
        phone=row.phone,
        postal_code=row._postal_code,
    )


def _row_to_supplier_dto(row: RowProxy) -> StoreSupplierResponseDto:
    return StoreSupplierResponseDto(
        supplier_id=row.supplier_id,
        supplier_name=row.supplier_name,
        contact_name=row.contact_name,
        contact_phone=row.contact_phone,
        disabled=row.disabled
    )
