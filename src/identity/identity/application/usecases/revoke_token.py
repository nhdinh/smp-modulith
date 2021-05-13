#!/usr/bin/env python
# -*- coding: utf-8 -*-
from identity.application.services.authentication_unit_of_work import AuthenticationUnitOfWork
from identity.domain.entities.revoked_token import RevokedToken


class RevokingTokenUC:
    def __init__(self,
                 uow: AuthenticationUnitOfWork) -> None:
        self._uow = uow

    def execute(self, token: RevokedToken) -> None:
        with self._uow as uow:  # type:AuthenticationUnitOfWork
            try:
                uow.identities.add_revoked_token(token)
                uow.commit()
            except Exception as exc:
                raise exc
