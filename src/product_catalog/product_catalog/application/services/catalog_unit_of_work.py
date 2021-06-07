#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy.orm import Session

from foundation.uow import SqlAlchemyUnitOfWork
from product_catalog import SqlAlchemyCatalogRepository


class CatalogUnitOfWork(SqlAlchemyUnitOfWork):
    def __init__(self, sessionfactory):
        super(CatalogUnitOfWork, self).__init__(sessionfactory=sessionfactory)

    def __enter__(self):
        self._session = self._sf()  # type: Session
        self._catalog_repo = SqlAlchemyCatalogRepository(session=self._session)
        return super(CatalogUnitOfWork, self).__enter__()

    def _commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()

    @property
    def catalogs(self) -> SqlAlchemyCatalogRepository:
        return self._catalog_repo
