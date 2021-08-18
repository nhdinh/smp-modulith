#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from foundation.value_objects.address import Address
from inventory.domain.entities.value_objects import AddressType


@dataclass
class WarehouseAddress:
  recipient: str
  phone: str
  address_type: AddressType
  address: Address

  @property
  def street_address(self):
    return self.address.street_address

  # @property
  # def sub_division_name(self):
  #     return self._sub_division_name
  #
  # @property
  # def division_name(self):
  #     return self._division_name
  #
  # @property
  # def city_name(self):
  #     return self._city_name
  #
  # @property
  # def country_name(self):
  #     return self._country_name
  #
  # @property
  # def iso_code(self):
  #     return self._iso_code

  @property
  def postal_code(self):
    return self.address.postal_code

  @property
  def full_address(self):
    # return f"{self._street_address}, {self._sub_division_name}, {self._division_name}, {self._city_name}, {self._country_name}"
    return f"{self.street_address}, {self.address.ward_code}"

  # def __eq__(self, other):
  #     if other is None or not isinstance(other, WarehouseAddress):
  #         return False
  #
  #     return self.full_address == other.full_address and self.recipient == other.recipient and self.phone == other.phone and self._postal_code == other._postal_code
  #
  # def __hash__(self):
  #     return hash(self.full_address + self.recipient + self.phone + self.postal_code)
