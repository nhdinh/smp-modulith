#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List

import marshmallow as ma

from db_infrastructure import GUID
from store.domain.entities.store_address import StoreAddressType


@dataclass
class StoreSettingResponseDto:
    name: str
    value: str
    type: str

    def serialize(self):
        return {
            'name': self.name,
            'value': self.value,
            'type': self.type,
        }


@dataclass
class StoreInfoResponseDto:
    store_id: GUID
    store_name: str
    # settings: List[StoreSettingResponseDto] = field(default_factory=list)
    settings: List[StoreSettingResponseDto] = field(metadata={"marshmallow_field": ma.fields.Raw()},
                                                    default_factory=list)

    def serialize(self):
        return {
            'store_id': str(self.store_id),
            'store_name': self.store_name,
            'settings': [setting.serialize() for setting in self.settings]
        }


@dataclass
class StoreWarehouseResponseDto:
    warehouse_id: GUID
    warehouse_name: str
    default: bool
    disabled: bool

    def serialize(self):
        return {
            'warehouse_id': str(self.warehouse_id),
            'warehouse_name': self.warehouse_name,
            'default': self.default,
            'disabled': self.disabled
        }


@dataclass
class StoreAddressResponseDto:
    store_address_id: str
    full_address: str
    street_address: str
    sub_division_name: str
    division_name: str
    city_name: str
    country_name: str
    iso_code: str
    address_type: StoreAddressType
    recipient: str
    phone: str
    postal_code: str

    def serialize(self):
        return {
            'store_address_id': self.store_address_id,
            'full_address': self.full_address,
            'street_address': self.street_address,
            'sub_division_name': self.sub_division_name,
            'division_name': self.division_name,
            'city_name': self.city_name,
            'country_name': self.country_name,
            'iso_code': self.iso_code,

            'address_type': self.address_type,
            'recipient': self.recipient,
            'phone': self.phone,
            'postal_code': self.postal_code
        }


