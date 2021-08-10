#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Union

from flask_jwt_extended import create_access_token, create_refresh_token

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
    mobile: str
    profile_image:str
    last_login_at:datetime
    created_at: datetime
    updated_at: datetime
    system_role: Role
    access_token: str
    refresh_token: str

    def serialize(self):
        return self.__dict__


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
                if user.failed_login_count >= 5 and user.last_login_at and datetime.now() - user.last_login_at < timedelta(
                        minutes=5):
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
                        mobile=user.mobile,
                        profile_image=user.profile_image if hasattr(user, 'profile_image') else '',
                        last_login_at=user.last_login_at,
                        created_at=user.created_at,
                        updated_at=user.updated_at,
                        system_role=user.system_role,
                        access_token=create_access_token(identity=user.user_id, additional_claims={
                            'system_role': user.system_role.role_name
                        }),
                        refresh_token=create_refresh_token(identity=user.user_id)
                    )
                    self._ob.present(output_dto)

                    uow.commit()
            except Exception as exc:
                raise exc
