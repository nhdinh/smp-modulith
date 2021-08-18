#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass


# from typing import NewType, Set

# StoreProductBrandReference = NewType('StoreProductBrandReference', tp=str)


@dataclass(unsafe_hash=True)
class ShopProductBrand:
    name: str
    logo: str = None

    def __eq__(self, other):
        if not other or not isinstance(other, ShopProductBrand):
            raise TypeError

        return self.name == other.name
