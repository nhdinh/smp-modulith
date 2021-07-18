#!/usr/bin/env python
# -*- coding: utf-8 -*-

from identity.application.services.authentication_unit_of_work import AuthenticationUnitOfWork
from identity.domain.entities import User


class IdentityHandlerFacade:
    def __init__(self, uow: AuthenticationUnitOfWork):
        self._uow = uow

    def create_user(self, email: str, mobile: str, hashed_password: str):
        with self._uow as uow:  # type: AuthenticationUnitOfWork
            try:
                user = User.create(email=email, password=hashed_password, is_plain_password=False, mobile=mobile)
                self._uow.identities.save(user)

                uow.commit()
            except Exception as exc:
                raise exc
