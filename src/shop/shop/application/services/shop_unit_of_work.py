#!/usr/bin/env python
# -*- coding: utf-8 -*-

from foundation.uow import SqlAlchemyUnitOfWork

from shop.application.shop_repository import SqlAlchemyShopRepository


class ShopUnitOfWork(SqlAlchemyUnitOfWork):
  def __init__(self, sessionfactory, event_bus):
    super(ShopUnitOfWork, self).__init__(sessionfactory=sessionfactory, event_bus=event_bus)

  def __enter__(self):
    super(ShopUnitOfWork, self).__enter__()
    self._shop_repo = SqlAlchemyShopRepository(session=self._session)

    return self

  def _commit(self):
    self._session.commit()

  def rollback(self):
    self._session.rollback()

  @property
  def shops(self) -> SqlAlchemyShopRepository:
    return self._shop_repo
