#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass


# from typing import NewType, Set

# StoreProductBrandReference = NewType('StoreProductBrandReference', tp=str)


@dataclass(unsafe_hash=True)
class StoreProductBrand:
    name: str
    logo: str = None
