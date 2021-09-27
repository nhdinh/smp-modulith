#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection

from foundation import EventBus
from pricing.services.pricing_handler_facade import PricingHandlerFacade
from pricing.services.pricing_uow import PricingUnitOfWork


class PricingEventHandlerModule(injector.Module):
    @injector.provider
    def facade(self, uow: PricingUnitOfWork, conn: Connection, event_bus: EventBus) -> PricingHandlerFacade:
        return PricingHandlerFacade(uow, conn, event_bus)
