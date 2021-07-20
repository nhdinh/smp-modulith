#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.uow import SqlAlchemyUnitOfWork

from identity.application.repositories.identity_repository import SqlAlchemyIdentityRepository


class IdentityUnitOfWork(SqlAlchemyUnitOfWork):
    def __init__(self, sessionfactory, event_bus):
        super(IdentityUnitOfWork, self).__init__(sessionfactory=sessionfactory, event_bus=event_bus)

    def __enter__(self):
        super(IdentityUnitOfWork, self).__enter__()
        self._identity_repo = SqlAlchemyIdentityRepository(session=self._session)

        return self

    def _commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()

    @property
    def identities(self) -> SqlAlchemyIdentityRepository:
        return self._identity_repo
