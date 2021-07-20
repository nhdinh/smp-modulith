#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.engine.row import RowProxy

from store.application.queries.response_dtos import (
    StoreAddressResponseDto,
    StoreInfoResponseDto,
    StoreSettingResponseDto,
    StoreWarehouseResponseDto,
)


def _row_to_store_settings_dto(row: RowProxy) -> StoreSettingResponseDto:
    return StoreSettingResponseDto(
        name=row.setting_key,
        value=row.setting_value,
        type=row.setting_type,
    )


def _row_to_store_info_dto(store_row_proxy: RowProxy) -> StoreInfoResponseDto:
    return StoreInfoResponseDto(
        store_id=store_row_proxy.shop_id,
        store_name=store_row_proxy.name,
        settings=[]
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
        store_address_id=row.shop_address_id,
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


