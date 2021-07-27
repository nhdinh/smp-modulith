#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from foundation import ThingGoneInBlackHoleError
from identity.application.services.identity_unit_of_work import IdentityUnitOfWork
from identity.domain.entities import User
from identity.domain.value_objects import UserEmail, UserId, ExceptionMessages


@dataclass
class LoggingUserInRequest:
    username: UserEmail
    password: str
    current_ip: str


@dataclass
class LoggedUserResponse:
    user_id: UserId
    email: UserEmail


class LoggingUserInResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: LoggedUserResponse) -> None:
        raise NotImplementedError


class LoggingUserInUC:
    def __init__(self,
                 output_boundary: LoggingUserInResponseBoundary,
                 uow: IdentityUnitOfWork):
        self._ob = output_boundary
        self._uow = uow

    def execute(self, input_dto: LoggingUserInRequest) -> None:
        with self._uow as uow:  # type: IdentityUnitOfWork
            try:
                user = uow.identities.get_user(query=input_dto.username)  # type: User
                if not user:
                    raise ThingGoneInBlackHoleError(ExceptionMessages.USER_NOT_FOUND)

                if not user.verify_password(input_dto.password):
                    raise Exception('Password mismatch')

                # update user login
                user.update_login_status(remote_address=input_dto.current_ip)

                # prepare output dto
                output_dto = LoggedUserResponse(
                    user_id=user.user_id,
                    email=user.email
                )
                self._ob.present(output_dto)
                uow.commit()
            except Exception as exc:
                raise exc
