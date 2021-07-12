#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from passlib.hash import pbkdf2_sha256 as sha256

from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.services.user_counter_services import UserCounters
from store.domain.entities.shop_registration import ShopRegistration


@dataclass
class RegisteringStoreRequest:
    store_name: str
    mobile: str
    email: str
    password: str


@dataclass
class RegisteringStoreResponse:
    registration_id: str


class RegisteringStoreResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: RegisteringStoreResponse) -> None:
        raise NotImplementedError


class RegisterStoreUC:
    def __init__(
            self,
            ob: RegisteringStoreResponseBoundary,
            uow: StoreUnitOfWork,
            user_counter_services: UserCounters):
        self._ob = ob
        self._uow = uow
        self.user_counter_services = user_counter_services

    def execute(self, dto: RegisteringStoreRequest):
        with self._uow as uow:
            try:
                # parse request data
                store_registration = ShopRegistration.create_registration(
                    shop_name=dto.store_name,
                    owner_email=dto.email,
                    owner_password=sha256.hash(dto.password),
                    owner_mobile=dto.mobile,
                    user_counter_services=self.user_counter_services
                )

                uow.stores.save_registration(store_registration)  # type: ignore

                # output dto
                output_dto = RegisteringStoreResponse(registration_id=store_registration.registration_id)
                self._ob.present(output_dto)

                # save data
                uow.commit()
            except Exception as exc:
                raise exc
