#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass

from vietnam_provinces import Province, Ward, District

from foundation.value_objects.address import Address
from shop.domain.entities.value_objects import AddressType


@dataclass(unsafe_hash=True)
class ShopAddress:
  recipient: str
  phone: str
  address_type: AddressType
  address: Address

  @property
  def street_address(self):
    return self.address.street_address

  @property
  def ward_code(self):
    return self.address.ward_code if self.address else None

  @property
  def ward(self) -> Ward:
    return self.address.ward if self.address else None

  @property
  def district_code(self):
    return self.address.district_code if self.address else None

  @property
  def district(self) -> District:
    return self.address.district if self.address else None

  @property
  def province_code(self):
    return self.address.province_code if self.address else None

  @property
  def province(self) -> Province:
    return self.address.province if self.address else None

  @property
  def postal_code(self):
    return self.address.postal_code

  def __eq__(self, other):
    if not isinstance(other, ShopAddress):
      return False
    else:
      return self.address == other.address and self.recipient == other.recipient and self.phone == other.phone and self.address_type == other.address_type
