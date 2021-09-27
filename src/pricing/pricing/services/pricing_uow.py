#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.uow import SqlAlchemyUnitOfWork
from pricing.services.pricing_repository import SqlAlchemyPricingRepository


class PricingUnitOfWork(SqlAlchemyUnitOfWork):
    def __init__(self, sessionfactory, event_bus):
        super(PricingUnitOfWork, self).__init__(sessionfactory=sessionfactory, event_bus=event_bus)

    def __enter__(self):
        super(PricingUnitOfWork, self).__enter__()
        self._pricing_repo = SqlAlchemyPricingRepository(session=self._session)

        return self

    def _commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()

    @property
    def prices(self) -> SqlAlchemyPricingRepository:
        return self._pricing_repo
