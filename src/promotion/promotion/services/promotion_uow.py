#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.uow import SqlAlchemyUnitOfWork


class PromotionUnitOfWork(SqlAlchemyUnitOfWork):
    def __init__(self, sessionfactory, event_bus):
        super(PromotionUnitOfWork, self).__init__(sessionfactory=sessionfactory, event_bus=event_bus)

    def __enter__(self):
        super(PromotionUnitOfWork, self).__enter__()
        self._promo_repo = SqlAlchemyPromotionRepository(session=self._session)
        return self

    def _commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()

    @property
    def shops(self) -> SqlAlchemyPromotionRepository:
        return self._promo_repo

