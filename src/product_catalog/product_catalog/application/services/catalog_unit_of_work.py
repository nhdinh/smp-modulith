#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from foundation.uow import SqlAlchemyUnitOfWork
from product_catalog import SqlAlchemyCatalogRepository


class CatalogUnitOfWork(SqlAlchemyUnitOfWork):
  def __init__(self, sessionfactory, event_bus):
    super(CatalogUnitOfWork, self).__init__(sessionfactory=sessionfactory, event_bus=event_bus)

  def __enter__(self):
    super(CatalogUnitOfWork, self).__enter__()
    self._catalog_repo = SqlAlchemyCatalogRepository(session=self._session)

    return self

  def _commit(self):
    self._session.commit()

  def rollback(self):
    self._session.rollback()

  @property
  def catalogs(self) -> SqlAlchemyCatalogRepository:
    return self._catalog_repo
