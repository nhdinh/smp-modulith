#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

from foundation.value_objects.address import LocationAddress, LocationCitySubDivision
from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.usecases.store_uc_common import get_shop_or_raise, get_location


@dataclass
class CreatingStoreAddressResponse:
    status: bool


class CreatingStoreAddressResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: CreatingStoreAddressResponse):
        raise NotImplementedError


@dataclass
class CreatingStoreAddressRequest:
    current_user: str

    recipient: str
    phone: str
    postal_code: str

    street_address: str
    sub_division_id: str

    division_id: Optional[str] = ''
    city_id: Optional[str] = ''
    country_id: Optional[str] = ''


class CreateStoreAddressUC:
    def __init__(self, boundary: CreatingStoreAddressResponseBoundary, uow: StoreUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: CreatingStoreAddressRequest) -> None:
        with self._uow as uow:  # type:StoreUnitOfWork
            try:
                store = get_shop_or_raise(store_owner=dto.current_user, uow=uow)

                sub_division = get_location(sub_division_id=dto.sub_division_id,
                                            uow=uow)  # type:LocationCitySubDivision
                if not sub_division:
                    raise ValueError('Cannot get address location')

                address = LocationAddress(
                    street_address=dto.street_address,
                    postal_code=dto.postal_code,
                    sub_division=sub_division,
                    division=sub_division.city_division,
                    city=sub_division.city_division.city,
                    country=sub_division.city_division.city.country,
                )
                store_address_id = store.add_address(
                    recipient=dto.recipient,
                    phone=dto.phone,
                    address=address
                )

                response = CreatingStoreAddressResponse(True)
                self._ob.present(response_dto=response)

                store.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
