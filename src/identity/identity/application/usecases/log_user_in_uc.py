#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Union

from foundation import ThingGoneInBlackHoleError
from identity.application.services.identity_unit_of_work import IdentityUnitOfWork
from identity.domain.entities import User, Role
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
    system_role: Role

    def serialize(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'system_role': self.system_role.role_name,
        }


@dataclass
class FailedLoginResponse:
    message: str

    def serialize(self):
        return self.__dict__


class LoggingUserInResponseBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, response_dto: Union[LoggedUserResponse, FailedLoginResponse]) -> None:
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

                # check user login failed count

                if user.failed_login_count >= 5 and user.last_login_at and datetime.now() - user.last_login_at < timedelta(minutes=5):
                    output_dto = FailedLoginResponse(message=ExceptionMessages.FAILED_LOGIN_EXCEED.value)
                    self._ob.present(output_dto)
                    return

                if not user.verify_password(input_dto.password):
                    # record failed logged in
                    user.failed_login_count += 1
                    user.last_login_at = datetime.now()
                    user.last_login_ip = input_dto.current_ip

                    # then raise an exception
                    # raise Exception('Password mismatch')
                    output_dto = FailedLoginResponse(message=ExceptionMessages.PASSWORD_MISMATCH.value)
                    self._ob.present(output_dto)

                    uow.commit()
                else:
                    # update user login
                    user.update_login_status(remote_address=input_dto.current_ip)

                    # prepare output dto
                    output_dto = LoggedUserResponse(
                        user_id=user.user_id,
                        email=user.email,
                        system_role=user.system_role,
                    )
                    self._ob.present(output_dto)

                    uow.commit()
            except Exception as exc:
                raise exc
