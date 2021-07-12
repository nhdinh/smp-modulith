#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.domain.entities.registration_status import RegistrationStatus
from store.domain.entities.shop_registration import ShopRegistration
from store.domain.entities.value_objects import ShopId


@dataclass
class ConfirmingStoreRegistrationRequest:
    confirmation_token: str


@dataclass
class ConfirmingStoreRegistrationResponse:
    store_id: ShopId
    status: bool


class ConfirmingStoreRegistrationResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: ConfirmingStoreRegistrationResponse) -> None:
        raise NotImplementedError


class ConfirmStoreRegistrationUC:
    def __init__(
            self,
            ob: ConfirmingStoreRegistrationResponseBoundary,
            uow: StoreUnitOfWork
    ):
        self._ob = ob
        self._uow = uow

    def execute(self, confirmation_token: str):
        with self._uow as uow:  # type: StoreUnitOfWork
            try:
                store_registration = uow.shops.fetch_registration_by_token(
                    token=confirmation_token
                )  # type: ShopRegistration
                if not store_registration:
                    raise Exception('Registration not existed')

                if store_registration.status != RegistrationStatus.REGISTRATION_WAITING_FOR_CONFIRMATION:
                    raise Exception('Invalid registration')

                # create the entity
                owner = store_registration.create_shop_user()
                store = store_registration.create_store(shop_admin=owner)
                warehouse = store_registration.create_default_warehouse(store_id=store.shop_id, owner=owner)

                # add warehouse to store
                store.warehouses.add(warehouse)
                store_id = store_registration.confirm()

                # persist into database
                uow.shops.save(store)

                dto = ConfirmingStoreRegistrationResponse(store_id=store_id, status=True)
                self._ob.present(dto)

                store.version += 1

                uow.commit()
            except Exception as exc:
                raise exc
