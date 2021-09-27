#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.engine import Connection

from foundation import EventBus
from pricing.services.pricing_uow import PricingUnitOfWork
from shop.application.services.shop_unit_of_work import ShopUnitOfWork


class PricingHandlerFacade:
    def __init__(self, uow: PricingUnitOfWork, conn: Connection, event_bus: EventBus):
        self._conn = conn
        self._uow = uow
        self._event_bus = event_bus
