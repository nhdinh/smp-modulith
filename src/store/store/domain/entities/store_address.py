#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from enum import Enum
from typing import NewType
from uuid import UUID

from foundation.value_objects.address import LocationAddress, LocationCitySubDivision

StoreAddressId = NewType('StoreAddressId', tp=UUID)


class StoreAddressType(Enum):
    STORE_ADDRESS = 'STORE_ADDRESS'
    WAREHOUSE_ADDRESS = 'WAREHOUSE_ADDRESS'


@dataclass
class StoreAddress:
    recipient: str
    phone: str
    address_type: StoreAddressType
    location_address: LocationAddress

    @property
    def street_address(self):
        return self._street_address

    @property
    def sub_division_name(self):
        return self._sub_division_name

    @property
    def division_name(self):
        return self._division_name

    @property
    def city_name(self):
        return self._city_name

    @property
    def country_name(self):
        return self._country_name

    @property
    def iso_code(self):
        return self._iso_code

    @property
    def postal_code(self):
        return self._postal_code

    @property
    def full_address(self):
        return f"{self._street_address}, {self._sub_division_name}, {self._division_name}, {self._city_name}, {self._country_name}"

    def __eq__(self, other):
        if other is None or not isinstance(other, StoreAddress):
            return False

        return self.full_address == other.full_address and self.recipient == other.recipient and self.phone == other.phone and self._postal_code == other._postal_code

    def __hash__(self):
        return hash(self.full_address + self.recipient + self.phone + self.postal_code)
