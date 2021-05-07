#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.uow import SqlAlchemyUnitOfWork


class CatalogUnitOfWork(SqlAlchemyUnitOfWork):
    def __init__(self, sessionfactory):
        super(CatalogUnitOfWork, self).__init__(sessionfactory=sessionfactory)

    def _collect_new_events(self):
        pass

    @property
    def session(self):
        return self._session
