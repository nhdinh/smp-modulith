#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.services.store_unit_of_work import ShopUnitOfWork
from store.domain.entities.registration_status import RegistrationStatus
from store.domain.entities.shop_registration import ShopRegistration
from store.domain.entities.value_objects import ShopId


@dataclass
class ConfirmingShopRegistrationRequest:
    confirmation_token: str


@dataclass
class ConfirmingShopRegistrationResponse:
    shop_id: ShopId
    status: bool


class ConfirmingShopRegistrationResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: ConfirmingShopRegistrationResponse) -> None:
        raise NotImplementedError


class ConfirmShopRegistrationUC:
    def __init__(
            self,
            ob: ConfirmingShopRegistrationResponseBoundary,
            uow: ShopUnitOfWork
    ):
        self._ob = ob
        self._uow = uow

    def execute(self, confirmation_token: str):
        with self._uow as uow:  # type: ShopUnitOfWork
            try:
                shop_registration = uow.shops.get_registration_by_token(
                    token=confirmation_token
                )  # type: ShopRegistration
                if not shop_registration:
                    raise Exception('Registration not existed')

                if shop_registration.status != RegistrationStatus.REGISTRATION_WAITING_FOR_CONFIRMATION:
                    raise Exception('Invalid registration')

                # create the entity
                owner = shop_registration.generate_shop_admin()
                shop = shop_registration.generate_shop(shop_admin=owner)
                warehouse = shop_registration.create_default_warehouse(store_id=shop.shop_id, owner=owner)

                # add warehouse to store
                shop.warehouses.add(warehouse)
                shop_registration.confirm()

                # persist into database
                uow.shops.save(shop)

                dto = ConfirmingShopRegistrationResponse(shop_id=shop.shop_id, status=True)
                self._ob.present(dto)

                shop.version += 1

                uow.commit()
            except Exception as exc:
                raise exc
