#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass

from identity.application.services.identity_unit_of_work import IdentityUnitOfWork
from identity.domain.value_objects import UserEmail


@dataclass
class RequestingToChangePasswordRequest:
    email: UserEmail


@dataclass
class RequestingToChangePasswordResponse:
    status: bool

    def serialize(self):
        return {
            'status': self.status
        }


class RequestingToChangePasswordResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: RequestingToChangePasswordResponse) -> None:
        raise NotImplementedError


class RequestToChangePasswordUC:
    def __init__(self, ob: RequestingToChangePasswordResponseBoundary, uow: IdentityUnitOfWork):
        self._ob = ob
        self._uow = uow

    def execute(self, input_dto: RequestingToChangePasswordRequest) -> None:
        with self._uow as uow:  # type: IdentityUnitOfWork
            try:
                user = uow.identities.get_user(query=input_dto.email)
                if not user:
                    raise Exception('User not found')

                user.create_new_password_change_token()

                dto = RequestingToChangePasswordResponse(status=True)
                self._ob.present(dto)

                uow.commit()
            except Exception as exc:
                raise exc
