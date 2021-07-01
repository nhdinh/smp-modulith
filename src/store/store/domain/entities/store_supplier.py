#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from uuid import UUID

from typing import NewType

StoreSupplierId = NewType('StoreSupplierId', tp=UUID)


@dataclass(unsafe_hash=True)
class SupplierContact:
    contact_name: str
    contact_phone: str


@dataclass(unsafe_hash=True)
class StoreSupplier:
    supplier_name: str
    contact_name: str
    contact_phone: str

    # contacts: FrozenSet[SupplierContact] = frozenset()
    disabled: bool = False
