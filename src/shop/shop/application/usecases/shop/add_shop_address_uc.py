#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.usecases.shop_uc_common import get_shop_or_raise
from shop.domain.entities.value_objects import ShopAddressId, ExceptionMessages
from web_app.serialization.dto import BaseShopInputDto


@dataclass
class AddingShopAddressRequest(BaseShopInputDto):
    pass


@dataclass
class AddingShopAddressResponse:
    shop_address_id: ShopAddressId


class AddingShopAddressResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: AddingShopAddressResponse) -> None:
        raise NotImplementedError


class AddShopAddressUC:
    def __init__(self, ob: AddingShopAddressResponseBoundary, uow: ShopUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, dto: AddingShopAddressRequest):
        with self._uow as uow:  # type:ShopUnitOfWork
            try:
                shop = get_shop_or_raise(shop_id=dto.shop_id, partner_id=dto.partner_id, uow=uow)

                if shop.is_catalog_exists(title=dto.name):
                    raise Exception(ExceptionMessages.STORE_CATALOG_EXISTED)
            except Exception as exc:
                raise exc
