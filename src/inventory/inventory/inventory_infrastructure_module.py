#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker

from foundation.events import EventBus

from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork


class InventoryInfrastructureModule(injector.Module):
    @injector.provider
    def get_uow(self, conn: Connection, event_bus: EventBus) -> InventoryUnitOfWork:
        sessfactory = sessionmaker(bind=conn)
        return InventoryUnitOfWork(sessionfactory=sessfactory, event_bus=event_bus)


"""
    @injector.provider
    def fetch_all_products_balance_query(self, conn: Connection) -> ListProductsBalanceQuery:
        return SqlListProductsBalanceQuery(connection=conn)

    @injector.provider
    def list_draft_purchase_orders_query(self, conn: Connection) -> ListDraftPurchaseOrdersQuery:
        return SqlListDraftPurchaseOrdersQuery(connection=conn)
"""
