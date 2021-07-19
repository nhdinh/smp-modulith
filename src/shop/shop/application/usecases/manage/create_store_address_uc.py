#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional


from foundation.value_objects.address import LocationAddress, LocationCitySubDivision
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise, get_location


@dataclass
class CreatingShopAddressResponse:
    status: bool


class CreatingShopAddressResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: CreatingShopAddressResponse):
        raise NotImplementedError


@dataclass
class CreatingShopAddressRequest:
    current_user: str

    recipient: str
    phone: str
    postal_code: str

    street_address: str
    sub_division_id: str

    division_id: Optional[str] = ''
    city_id: Optional[str] = ''
    country_id: Optional[str] = ''


class CreateShopAddressUC:
    def __init__(self, boundary: CreatingShopAddressResponseBoundary, uow: ShopUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: CreatingShopAddressRequest) -> None:
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                shop = get_shop_or_raise(store_owner=dto.current_user, uow=uow)

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
                shop_address_id = shop.add_address(
                    recipient=dto.recipient,
                    phone=dto.phone,
                    address=address
                )

                response = CreatingShopAddressResponse(True)
                self._ob.present(response_dto=response)

                shop.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
