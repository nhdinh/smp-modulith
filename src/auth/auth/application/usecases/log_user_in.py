#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from auth.application.services.authentication_unit_of_work import AuthenticationUnitOfWork
from auth.domain.entities import User
from auth.domain.value_objects import UserEmail, UserId


@dataclass
class LoggingUserInRequest:
    username: UserEmail
    password: str


@dataclass
class LoggedUserResponse:
    id: UserId
    username: UserEmail


class LoggingUserInResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: LoggedUserResponse) -> None:
        raise NotImplementedError


class LoggingUserInUC:
    def __init__(self,
                 output_boundary: LoggingUserInResponseBoundary,
                 uow: AuthenticationUnitOfWork):
        self._ob = output_boundary
        self._uow = uow

    def execute(self, input_dto: LoggingUserInRequest) -> None:
        with self._uow as uow:  # type: AuthenticationUnitOfWork
            try:
                user = uow.identities.fetch_user(query=input_dto.username)  # type:User
                if not user:
                    raise Exception('User not found')

                if not user.verify_password(input_dto.password):
                    raise Exception('Password mismatch')

                # update user login
                login_count = 1

                # prepare output dto
                output_dto = LoggedUserResponse(
                    id=user.id,
                    username=user.email
                )
                self._ob.present(output_dto)
                uow.commit()
            except Exception as exc:
                raise exc
