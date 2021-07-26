#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from vietnam_provinces.enums.wards import WardEnum, WardDEnum

from foundation.events import WillRaiseExceptionEvent, new_event_id
from foundation.value_objects.address import Address
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.shop import Shop
from shop.domain.entities.value_objects import ShopAddressId
from web_app.serialization.dto import BaseAuthorizedShopUserRequest


@dataclass
class AddingShopAddressResponse:
    shop_address_id: ShopAddressId


class AddingShopAddressResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: AddingShopAddressResponse):
        raise NotImplementedError


@dataclass
class AddingShopAddressRequest(BaseAuthorizedShopUserRequest):
    recipient: str
    phone: str
    postal_code: str
    street_address: str

    ward_code: str


class AddShopAddressUC:
    def __init__(self, boundary: AddingShopAddressResponseBoundary, uow: ShopUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: AddingShopAddressRequest) -> None:
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                shop = get_shop_or_raise(shop_id=dto.shop_id, user_id=dto.current_user_id, uow=uow)  # type:Shop

                ward = WardEnum[f'{dto.ward_code}'].value
                if not ward:
                    raise ValueError('Cannot get address location')

                address = Address(
                    street_address=dto.street_address,
                    postal_code=dto.postal_code,
                    ward_code=dto.ward_code
                )

                shop_address = shop.add_address(
                    recipient=dto.recipient,
                    phone=dto.phone,
                    address=address
                )

                response = AddingShopAddressResponse(shop_address_id=shop_address.shop_address_id)
                self._ob.present(response_dto=response)

                shop.version += 1
                uow.commit()
            except Exception as exc:
                raise exc
