#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List

import marshmallow as ma
from sqlalchemy.engine.row import RowProxy

from shop.domain.entities.value_objects import ShopId, ShopWarehouseId, AddressType


@dataclass
class ShopSettingResponseDto:
    name: str
    value: str
    type: str

    def serialize(self):
        return self.__dict__


@dataclass
class ShopInfoResponseDto:
    shop_id: ShopId
    store_name: str
    # settings: List[ShopSettingResponseDto] = field(default_factory=list)
    settings: List[ShopSettingResponseDto] = field(metadata={"marshmallow_field": ma.fields.Raw()},
                                                   default_factory=list)

    def serialize(self):
        return {
            'store_id': str(self.shop_id),
            'store_name': self.store_name,
            'settings': [setting.serialize() for setting in self.settings]
        }


@dataclass
class ShopWarehouseResponseDto:
    warehouse_id: ShopWarehouseId
    warehouse_name: str
    default: bool
    disabled: bool

    def serialize(self):
        return self.__dict__


@dataclass
class ShopAddressResponseDto:
    store_address_id: str
    full_address: str
    street_address: str
    sub_division_name: str
    division_name: str
    city_name: str
    country_name: str
    iso_code: str
    address_type: AddressType
    recipient: str
    phone: str
    postal_code: str

    def serialize(self):
        return self.__dict__


def _row_to_store_settings_dto(row: RowProxy) -> ShopSettingResponseDto:
    return ShopSettingResponseDto(
        name=row.setting_key,
        value=row.setting_value,
        type=row.setting_type,
    )


def _row_to_store_info_dto(store_row_proxy: RowProxy) -> ShopInfoResponseDto:
    return ShopInfoResponseDto(
        store_id=store_row_proxy.shop_id,
        store_name=store_row_proxy.name,
        settings=[]
    )


def _row_to_warehouse_dto(row: RowProxy) -> ShopWarehouseResponseDto:
    return ShopWarehouseResponseDto(
        warehouse_id=row.warehouse_id,
        warehouse_name=row.warehouse_name,
        default=row.default,
        disabled=row.disabled,
    )


def _row_to_address_dto(row: RowProxy) -> ShopAddressResponseDto:
    return ShopAddressResponseDto(
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
