#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import timedelta, datetime

from identity.domain.value_objects import UserEmail

from identity.domain.rules.password_must_meet_requirement_rule import PasswordMustMeetRequirementRule

from identity.application.services.authentication_unit_of_work import AuthenticationUnitOfWork
from identity.domain.entities import User


@dataclass
class ResettingPasswordRequest:
    reset_token: str
    new_password: str
    new_password_retype: str


@dataclass
class ChangingPasswordRequest:
    current_user: UserEmail
    old_password: str
    new_password: str
    new_password_retype: str


@dataclass
class ChangingPasswordResponse:
    email: UserEmail
    status: bool

    def serialize(self):
        return {
            'email': self.email,
            'status': self.status
        }


@dataclass
class ChangingPasswordResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: ChangingPasswordResponse) -> None:
        raise NotImplementedError


class ChangePasswordUC:
    def __init__(self, ob: ChangingPasswordResponseBoundary, uow: AuthenticationUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute_reset(self, input_dto: ResettingPasswordRequest) -> None:
        with self._uow as uow:  # type:AuthenticationUnitOfWork
            try:
                user = uow.identities.fetch_user_by_token(reset_password_token=input_dto.reset_token)  # type:User

                if not user:
                    raise Exception('User not found')

                if datetime.now() - user.request_reset_password_at > timedelta(days=1):
                    raise Exception('Token expired')

                if input_dto.new_password != input_dto.new_password_retype:
                    raise Exception('New password and retype are not matched.')

                # do change password
                user.change_password(new_password=input_dto.new_password)

                # build dto
                dto = ChangingPasswordResponse(email=user.email, status=True)
                self._ob.present(dto)

                uow.commit()
            except Exception as exc:
                raise exc

    def execute_change(self, input_dto: ChangingPasswordRequest) -> None:
        with self._uow as uow:  # type:AuthenticationUnitOfWork
            try:
                user = uow.identities.fetch_user(query=input_dto.current_user)

                if not user:
                    raise Exception('User not found')

                if not user.verify_password(input_dto.old_password):
                    raise Exception('Old password was wrong')

                if input_dto.new_password != input_dto.new_password_retype:
                    raise Exception('New password and retype are not matched.')

                # do change password
                user.change_password(new_password=input_dto.new_password)

                # build dto
                dto = ChangingPasswordResponse(email=user.email, status=True)
                self._ob.present(dto)

                uow.commit()
            except Exception as exc:
                raise exc
