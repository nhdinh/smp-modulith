#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass
class ShopProductCache:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
