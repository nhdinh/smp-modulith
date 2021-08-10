#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from typing import Optional

import sqlalchemy

from identity.application.services.identity_unit_of_work import IdentityUnitOfWork
from identity.domain.entities import User
from identity.domain.value_objects import UserEmail, UserId, ExceptionMessages
from web_app.serialization.dto import BaseTimeLoggedRequest


@dataclass
class RegisteringAccountRequest(BaseTimeLoggedRequest):
    email: UserEmail
    mobile: Optional[str]
    password: str


@dataclass
class RegisteringUserResponse:
    user_id: UserId
    email: UserEmail


class RegisteringAccountResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: RegisteringUserResponse) -> None:
        raise NotImplementedError


class RegisterAccountUC:
    def __init__(self,
                 output_boundary: RegisteringAccountResponseBoundary,
                 uow: IdentityUnitOfWork) -> None:
        self._ob = output_boundary
        self._uow = uow

    def execute(self, input_dto: RegisteringAccountRequest) -> None:
        with self._uow as uow:  # type:IdentityUnitOfWork
            try:
                user = User.create(email=input_dto.email, password=input_dto.password, mobile=input_dto.mobile,
                                   on_shop_confirmation=False)
                uow.identities.save(user)

                # output
                output_dto = RegisteringUserResponse(
                    user_id=user.user_id,
                    email=user.email,
                )
                self._ob.present(output_dto)

                # commit uow
                uow.commit()
            except sqlalchemy.exc.IntegrityError as exc:
                raise Exception(ExceptionMessages.USER_REGISTRATION_EXISTED)
            except Exception as exc:
                raise exc


class CreatingDefaultAdminUC:
    def __init__(self, output_boundary: RegisteringAccountResponseBoundary,
                 uow: IdentityUnitOfWork) -> None:
        self._ob = output_boundary
        self._uow = uow

    def execute(self):
        with self._uow as uow:
            pass
