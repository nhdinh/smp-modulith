#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List

import marshmallow as ma
from sqlalchemy.engine.row import RowProxy
from vietnam_provinces import Ward, District, Province
from vietnam_provinces.enums import DistrictEnum, ProvinceEnum
from vietnam_provinces.enums.wards import WardEnum

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
    shop_name: str
    # settings: List[ShopSettingResponseDto] = field(default_factory=list)
    settings: List[ShopSettingResponseDto] = field(metadata={"marshmallow_field": ma.fields.Raw()},
                                                   default_factory=list)

    def serialize(self):
        return {
            'shop_id': str(self.shop_id),
            'shop_name': self.shop_name,
            'settings': [setting.serialize() for setting in self.settings],
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
    postal_code: str
    ward_code: str

    recipient: str
    phone: str
    address_type: AddressType

    def serialize(self):
        ward = WardEnum[self.ward_code].value  # type:Ward
        district = DistrictEnum[f"D_{ward.district_code}"].value  # type:District
        province = ProvinceEnum[f"P_{district.province_code}"].value  # type:Province

        _d = self.__dict__
        _d.update({
            'ward': ward.name,
            'district': district.name,
            'province': province.name
        })

        return _d


def _row_to_store_settings_dto(row: RowProxy) -> ShopSettingResponseDto:
    return ShopSettingResponseDto(
        name=row.setting_key,
        value=row.setting_value,
        type=row.setting_type,
    )


def _row_to_shop_info_dto(store_row_proxy: RowProxy) -> ShopInfoResponseDto:
    return ShopInfoResponseDto(
        shop_id=store_row_proxy.shop_id,
        shop_name=store_row_proxy.name,
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
        full_address=f"{row.street_address}",
        street_address=row.street_address,
        postal_code=row.postal_code,
        ward_code=row.ward_code,
        address_type=row.address_type,
        recipient=row.recipient,
        phone=row.phone,
    )
