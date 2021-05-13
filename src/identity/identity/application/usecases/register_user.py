#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

import sqlalchemy.exc

from identity.application.services.authentication_unit_of_work import AuthenticationUnitOfWork
from identity.domain.entities import User
from identity.domain.value_objects import UserEmail, UserId


@dataclass
class RegisteringUserRequest:
    email: UserEmail
    password: str


@dataclass
class RegisteringUserResponse:
    id: UserId
    email: UserEmail


class RegisteringUserResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: RegisteringUserResponse) -> None:
        raise NotImplementedError


class RegisteringUserUC:
    def __init__(self,
                 output_boundary: RegisteringUserResponseBoundary,
                 uow: AuthenticationUnitOfWork) -> None:
        self._ob = output_boundary
        self._uow = uow

    def execute(self, input_dto: RegisteringUserRequest) -> None:
        with self._uow as uow:  # type:AuthenticationUnitOfWork
            try:
                user = User.create(email=input_dto.email, plain_password=input_dto.password)
                uow.identities.save(user)

                # output
                output_dto = RegisteringUserResponse(
                    id=user.id,
                    email=user.email,
                )
                self._ob.present(output_dto)

                # commit uow
                uow.commit()
            except Exception as exc:
                raise exc


class CreatingDefaultAdminUC:
    def __init__(self, output_boundary: RegisteringUserResponseBoundary,
                 uow: AuthenticationUnitOfWork) -> None:
        self._ob = output_boundary
        self._uow = uow

    def execute(self):
        with self._uow as uow:
            pass
