#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.uow import AbstractUnitOfWork


class InventoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self, sessionfactory, event_bus):
        super(InventoryUnitOfWork, self).__init__(sessionfactory=sessionfactory, event_bus=event_bus)

    def __enter__(self):
        super(InventoryUnitOfWork, self).__enter__()
        self._inventory_repo = SqlAlchemyInventoryRepository(session=self._session)

        return self

    def _commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()

    def _collect_new_events(self):
        pass

    @property
    def inventory(self) -> SqlAlchemyInventoryRepository:
        return self._inventory_repo
