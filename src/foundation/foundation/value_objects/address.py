#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from typing import Set


@dataclass(unsafe_hash=True)
class LocationCitySubDivision:
    sub_division_name: str
    city_division: 'LocationCityDivision'
    city: 'LocaltionCity'
    country: 'LocationCountry'


@dataclass(unsafe_hash=True)
class LocationCityDivision:
    division_name: str
    city: 'LocationCity'
    country: 'LocationCountry'


@dataclass(unsafe_hash=True)
class LocationCity:
    city_name: str
    provinces: Set[LocationCityDivision]
    country: 'LocationCountry'


@dataclass(unsafe_hash=True)
class LocationCountry:
    cities: Set[LocationCity]
    country_name: str
    iso_code: str


@dataclass(unsafe_hash=True)
class LocationAddress:
    address: str
    sub_division: LocationCitySubDivision
    division: LocationCityDivision
    city: LocationCity
    country: LocationCountry

    def __str__(self) -> str:
        return f"{self.address}, {self.sub_division}, {self.division}, {self.city}, {self.country}"
