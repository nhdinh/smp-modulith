#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.uow import SqlAlchemyUnitOfWork
from identity.application.repositories.identity_repository import SqlAlchemyIdentityRepository


class AuthenticationUnitOfWork(SqlAlchemyUnitOfWork):
    def __init__(self, sessionfactory):
        super(AuthenticationUnitOfWork, self).__init__(sessionfactory=sessionfactory)

    def __enter__(self):
        self._session = self._sf()  # type:Session
        self._identity_repo = SqlAlchemyIdentityRepository(session=self._session)
        return super(AuthenticationUnitOfWork, self).__enter__()

    def _collect_new_events(self):
        pass

    def _commit(self):
        self._session.commit()

    def rollback(self):
        pass

    @property
    def identities(self) -> SqlAlchemyIdentityRepository:
        return self._identity_repo
