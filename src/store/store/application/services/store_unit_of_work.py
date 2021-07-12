#!/usr/bin/env python
# -*- coding: utf-8 -*-

from foundation.uow import SqlAlchemyUnitOfWork
from store.application.store_repository import SqlAlchemyStoreRepository


class StoreUnitOfWork(SqlAlchemyUnitOfWork):
    def __init__(self, sessionfactory, event_bus):
        super(StoreUnitOfWork, self).__init__(sessionfactory=sessionfactory, event_bus=event_bus)

    def __enter__(self):
        super(StoreUnitOfWork, self).__enter__()
        self._store_repo = SqlAlchemyStoreRepository(session=self._session)

        return self

    def _commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()

    @property
    def shops(self) -> SqlAlchemyStoreRepository:
        return self._store_repo
