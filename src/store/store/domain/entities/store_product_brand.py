#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from typing import NewType, Set

StoreProductBrandReference = NewType('StoreProductBrandReference', tp=str)


@dataclass(unsafe_hash=True)
class StoreProductBrand:
    reference: StoreProductBrandReference
    display_name: str

    _products = None  # type: Set
    _store = None

    @property
    def store(self):
        return getattr(self, '_store', None)

    @store.setter
    def store(self, value):
        setattr(self, '_store', value)
