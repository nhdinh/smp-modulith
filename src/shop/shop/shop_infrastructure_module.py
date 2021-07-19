#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker

from foundation.events import EventBus
from shop.adapter import shop_db
from shop.application.services.shop_unit_of_work import ShopUnitOfWork


class ShopInfrastructureModule(injector.Module):
    @injector.provider
    def store_db(self) -> shop_db:
        return shop_db

    @injector.provider
    def get_uow(self, conn: Connection, event_bus: EventBus) -> ShopUnitOfWork:
        sessfactory = sessionmaker(bind=conn)
        return ShopUnitOfWork(sessionfactory=sessfactory, event_bus=event_bus)
