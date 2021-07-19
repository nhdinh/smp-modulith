#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.domain.entities.value_objects import ShopRegistrationId, RegistrationStatus
from web_app.presenters.shop_presenters import RegistrationStatusDto
from web_app.serialization.dto import BaseInputDto


@dataclass
class ConfirmingShopRegistrationRequest(BaseInputDto):
    confirmation_token: str


@dataclass
class ConfirmingShopRegistrationResponse:
    registration_id: ShopRegistrationId
    status: RegistrationStatusDto


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

    def execute(self, dto: ConfirmingShopRegistrationRequest):
        with self._uow as uow:  # type: ShopUnitOfWork
            try:
                shop_registration = uow.shops.get_registration_by_token(
                    token=dto.confirmation_token
                )  # type: ShopRegistration
                if not shop_registration:
                    raise Exception('Registration not existed')

                # TODO: Remove this
                # if shop_registration.status != RegistrationStatus.REGISTRATION_WAITING_FOR_CONFIRMATION:
                #     raise Exception('Invalid registration')

                # create the entity
                shop_registration.confirm()

                # owner = shop_registration.generate_shop_admin()
                # shop = shop_registration.create_shop(shop_admin=owner)
                # warehouse = shop_registration.create_default_warehouse(store_id=shop.shop_id, owner=owner)

                # add warehouse to store
                # shop.warehouses.add(warehouse)

                # persist into database

                dto = ConfirmingShopRegistrationResponse(registration_id=shop_registration.registration_id,
                                                         status=RegistrationStatusDto(shop_registration.status))
                self._ob.present(dto)

                shop_registration.version += 1

                uow.commit()
            except Exception as exc:
                raise exc
