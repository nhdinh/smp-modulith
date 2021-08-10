#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

import psycopg2
import sqlalchemy

from identity.domain.entities import User
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.services.shop_user_counters import ShopUserCounter
from shop.domain.entities.shop_registration import ShopRegistration
from shop.domain.entities.value_objects import ShopRegistrationId, ExceptionMessages
from web_app.serialization.dto import BaseTimeLoggedRequest


@dataclass
class RegisteringShopRequest(BaseTimeLoggedRequest):
    name: str
    email: str
    password: str
    mobile: Optional[str] = ''


@dataclass
class RegisteringShopResponse:
    registration_id: ShopRegistrationId


class RegisteringShopResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: RegisteringShopResponse) -> None:
        raise NotImplementedError


class RegisterShopUC:
    def __init__(
            self,
            ob: RegisteringShopResponseBoundary,
            uow: ShopUnitOfWork,
            user_counter_services: ShopUserCounter,
    ):
        self._ob = ob
        self._uow = uow
        self.user_counter_services = user_counter_services

    def execute(self, dto: RegisteringShopRequest):
        with self._uow as uow:
            try:
                # parse request data
                store_registration = ShopRegistration.create_registration(
                    shop_name=dto.name,
                    owner_email=dto.email,
                    owner_password=User.generate_hash(dto.password),
                    owner_mobile=dto.mobile,
                    user_counter_services=self.user_counter_services
                )

                uow.shops.save_registration(store_registration)  # type: ignore

                # output dto
                output_dto = RegisteringShopResponse(registration_id=store_registration.registration_id)
                self._ob.present(output_dto)

                # save data
                uow.commit()
            except sqlalchemy.exc.IntegrityError as exc:
                if hasattr(exc, 'orig') and isinstance(exc.orig, psycopg2.errors.UniqueViolation):
                    if 'owner_email' in exc.orig.pgerror:
                        raise Exception(ExceptionMessages.EMAIL_HAS_BEEN_REGISTERED)
                    elif 'owner_mobile' in exc.orig.pgerror:
                        raise Exception(ExceptionMessages.PHONE_NUMBER_HAS_BEEN_REGISTERED)
                # else, raise generic message
                raise exc
            except Exception as exc:
                raise exc
