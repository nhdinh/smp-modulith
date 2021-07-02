#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import NewType
from uuid import UUID

StoreSupplierId = NewType('StoreSupplierId', tp=UUID)


@dataclass(unsafe_hash=True)
class SupplierContact:
    contact_name: str
    contact_phone: str

    def __eq__(self, other):
        if not other or not isinstance(other, SupplierContact):
            raise TypeError

        return self.contact_phone == other.contact_name and self.contact_phone == other.contact_phone


@dataclass(unsafe_hash=True)
class StoreSupplier:
    supplier_name: str
    contact_name: str
    contact_phone: str

    # contacts: FrozenSet[SupplierContact] = frozenset()
    disabled: bool = False
