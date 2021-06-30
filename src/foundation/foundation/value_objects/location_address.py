#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class LocationAddress:
    address: str
    province: str
    city: str
    country: str

    def __str__(self) -> str:
        return f"{self.address}, {self.province}, {self.city}, {self.country}"
