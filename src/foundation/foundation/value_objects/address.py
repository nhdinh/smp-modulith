#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import NewType, Set

from db_infrastructure import nanoid_generate

LocationAddressId = NewType('LocationAddressId', tp=str)
LocationCountryId = NewType('LocationCountryId', tp=str)
LocationCityId = NewType('LocationCityId', tp=str)
LocationCityDivisionId = NewType('LocationCityDivisionId', tp=str)
LocationCitySubDivisionId = NewType('LocationCitySubDivisionId', tp=str)

COUNTRY_ID_PREFIX = 'Country'
CITY_ID_PREFIX = 'City'
DIVISION_ID_PREFIX = 'Div'
SUB_DIVISION_ID_PREFIX = 'SubDiv'
ADDRESS_ID_PREFIX = 'Address'


def generate_country_id():
    return nanoid_generate(prefix=COUNTRY_ID_PREFIX)


def generate_city_id():
    return nanoid_generate(prefix=CITY_ID_PREFIX)


def generate_division_id():
    return nanoid_generate(prefix=DIVISION_ID_PREFIX)


def generate_sub_division_id():
    return nanoid_generate(prefix=SUB_DIVISION_ID_PREFIX)


def generate_address_id():
    return nanoid_generate(prefix=ADDRESS_ID_PREFIX)


@dataclass
class LocationCitySubDivision:
    sub_division_name: str

    @property
    def city_division(self) -> 'LocationCityDivision':
        return self._city_division

    def __eq__(self, other):
        if not other or not isinstance(other, LocationCitySubDivision):
            raise TypeError

        return self.sub_division_name == other.sub_division_name and self.city_division == other.city_division

    def __str__(self):
        return f"<LocationCitySubDivision '{self.sub_division_name}, {self.city_division.division_name}, {self.city_division.city.city_name}, {self.city_division.city.country.country_name}'>"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.sub_division_id)


@dataclass
class LocationCityDivision:
    division_name: str
    sub_divisions: Set[LocationCitySubDivision] = frozenset()

    @property
    def city(self) -> 'LocationCity':
        return self._city

    def __eq__(self, other):
        if not other or not isinstance(other, LocationCityDivision):
            raise TypeError

        return self.division_name == other.division_name and self._city == other._city

    def __str__(self):
        return f"<LocationCityDivision '{self.division_name}, {self._city.city_name}, {self._city.country.country_name}'>"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.division_id)


@dataclass
class LocationCity:
    city_name: str
    divisions: Set[LocationCityDivision] = frozenset()

    @property
    def country(self) -> 'LocationCountry':
        return self._country

    def __eq__(self, other):
        if not other or not isinstance(other, LocationCity):
            raise TypeError

        return self.city_name == other.city_name and self._country == other._country

    def __str__(self):
        return f"<LocationCity '{self.city_name}, {self._country.country_name}'>"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.city_id)


@dataclass
class LocationCountry:
    country_name: str
    iso_code: str
    cities: Set[LocationCity] = frozenset()

    def __eq__(self, other):
        if not other or not isinstance(other, LocationCountry):
            raise TypeError

        return self.country_name == other.country_name or self.iso_code == other.iso_code

    def __str__(self):
        return f"<LocationCountry #{self.iso_code} '{self.country_name}'>"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.country_id)


@dataclass
class LocationAddress:
    street_address: str
    postal_code: str
    sub_division: LocationCitySubDivision
    division: LocationCityDivision = None
    city: LocationCity = None
    country: LocationCountry = None

    def __str__(self) -> str:
        return f"{self.address}, {self.sub_division}, {self.division}, {self.city}, {self.country}"

    def __hash__(self):
        return hash(self.address_id)
