#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import marshmallow as ma

from db_infrastructure import GUID
from store.domain.entities.store_address import StoreAddressType


@dataclass
class StoreProductTagResponseDto:
    tag: str

    def serialize(self):
        return {
            'tag': self.tag
        }


@dataclass
class StoreProductBrandResponseDto:
    brand_id: GUID
    brand_name: str
    logo: str

    def serialize(self):
        return self.__dict__


@dataclass
class StoreProductUnitResponseDto:
    unit_name: str
    default: bool
    referenced_unit_name: str
    conversion_factor: float

    def serialize(self):
        return self.__dict__


@dataclass
class StoreCollectionResponseDto:
    collection_id: GUID
    reference: str
    title: str
    is_collection_disabled: bool

    def serialize(self):
        return self.__dict__


@dataclass
class StoreCatalogResponseDto:
    catalog_id: GUID
    store_id: str
    reference: str
    title: str
    is_default_catalog: bool
    is_catalog_disabled: bool
    collections: List[StoreCollectionResponseDto]

    def serialize(self):
        return {
            'catalog_id': str(self.catalog_id),
            'store_id': str(self.store_id),
            'catalog_reference': self.reference,
            'catalog_title': self.title,
            'default': self.default,
            'disabled': self.disabled,
            'collection': [c.serialize() for c in self.collections]
        }


@dataclass
class StoreCatalogResponseCompactedDto:
    catalog_id: GUID
    catalog_reference: str
    catalog_title: str
    catalog_image: str
    is_catalog_disabled: bool

    def serialize(self):
        return self.__dict__


@dataclass
class StoreProductShortResponseDto:
    product_id: GUID
    reference: str
    title: str

    image: str

    brand: str
    catalog: str
    catalog_id: GUID
    created_at: datetime

    def serialize(self):
        return {
            'product_id': self.product_id,
            'title': self.title,
            'image': self.image if self.image else '',
            'catalog': self.catalog,
            'catalog_id': self.catalog_id,
            'brand': self.brand,
            'created_at': self.created_at
        }


@dataclass
class StoreProductResponseDto:
    product_id: GUID
    reference: str
    title: str

    brand: StoreProductBrandResponseDto
    catalog: StoreCatalogResponseCompactedDto
    created_at: datetime
    updated_at: datetime

    units: List[StoreProductUnitResponseDto]
    tags: List[StoreProductTagResponseDto]
    collections: List[StoreCollectionResponseDto]

    def serialize(self):
        return self.__dict__


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


@dataclass
class StoreSupplierResponseDto:
    supplier_id: str
    supplier_name: str
    contact_name: str
    contact_phone: str
    disabled: bool

    def serialize(self):
        return self.__dict__
