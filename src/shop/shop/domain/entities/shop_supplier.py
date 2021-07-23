#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from typing import Set

from shop.domain.entities.value_objects import GenericShopItemStatus


@dataclass
class SupplierContact:
    contact_name: str
    contact_phone: str
    status: GenericShopItemStatus

    def __eq__(self, other):
        if not other or not isinstance(other, SupplierContact):
            raise TypeError

        return self.contact_name == other.contact_name and self.contact_phone == other.contact_phone

    def __hash__(self):
        return hash((self.contact_name, self.contact_phone))


@dataclass
class ShopSupplier:
    supplier_name: str
    status: GenericShopItemStatus = GenericShopItemStatus.NORMAL

    @property
    def contacts(self) -> Set[SupplierContact]:
        _contacts = getattr(self, '_contacts', set())
        return _contacts

    @property
    def products(self):
        return self._products if hasattr(self, '_products') else []

    def __eq__(self, other):
        if not other or not isinstance(other, ShopSupplier):
            return False

        return self.supplier_name.lower() == other.supplier_name.lower()

    def __hash__(self):
        return hash(self.supplier_id)
