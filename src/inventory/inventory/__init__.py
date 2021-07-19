#!/usr/bin/env python
# -*- coding: utf-8 -*-

import injector
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker

from foundation.domain_events.shop_events import ShopCreatedEvent, ShopProductCreatedEvent
from foundation.events import EventBus, AsyncEventHandlerProvider, AsyncHandler, EveryModuleMustCatchThisEvent
from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from inventory.application.usecases.approve_purchase_order_uc import ApprovePurchaseOrderUC, \
    ApprovingPurchaseOrderResponseBoundary
from inventory.application.usecases.create_draft_purchase_order_uc import CreatingDraftPurchaseOrderResponseBoundary, \
    CreateDraftPurchaseOrderUC
from inventory.application.usecases.remove_draft_purchase_order_item_uc import RemoveDraftPurchaseOrderItemUC, \
    RemovingDraftPurchaseOrderItemResponseBoundary
from inventory.application.usecases.update_draft_purchase_order_uc import UpdatingDraftPurchaseOrderResponseBoundary, \
    UpdateDraftPurchaseOrderUC
from inventory.inventory_handler_facade import InventoryHandlerFacade, ShopProductCreatedEventHandler, \
    ShopCreatedEventHandler, Inventory_CatchAllEventHandler


class InventoryEventHandlerModule(injector.Module):
    @injector.provider
    def facade(self, uow: InventoryUnitOfWork) -> InventoryHandlerFacade:
        return InventoryHandlerFacade(uow=uow)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[EveryModuleMustCatchThisEvent],
                         to=AsyncEventHandlerProvider(Inventory_CatchAllEventHandler))

        binder.multibind(AsyncHandler[ShopCreatedEvent], to=AsyncEventHandlerProvider(ShopCreatedEventHandler))
        binder.multibind(AsyncHandler[ShopProductCreatedEvent],
                         to=AsyncEventHandlerProvider(ShopProductCreatedEventHandler))

    @injector.provider
    def create_draft_purchase_order(self, boundary: CreatingDraftPurchaseOrderResponseBoundary,
                                    uow: InventoryUnitOfWork) -> CreateDraftPurchaseOrderUC:
        return CreateDraftPurchaseOrderUC(boundary, uow)

    @injector.provider
    def create_draft_purchase_order_uc(self, boundary: CreatingDraftPurchaseOrderResponseBoundary,
                                       uow: InventoryUnitOfWork) -> CreateDraftPurchaseOrderUC:
        return CreateDraftPurchaseOrderUC(boundary, uow)

    @injector.provider
    def add_purchase_order_item(self, boundary: UpdatingDraftPurchaseOrderResponseBoundary,
                                uow: InventoryUnitOfWork) -> UpdateDraftPurchaseOrderUC:
        return UpdateDraftPurchaseOrderUC(boundary, uow)

    @injector.provider
    def approve_purchase_order_uc(self, boundary: ApprovingPurchaseOrderResponseBoundary,
                                  uow: InventoryUnitOfWork) -> ApprovePurchaseOrderUC:
        return ApprovePurchaseOrderUC(boundary, uow)

    @injector.provider
    def remove_draft_purchase_order_item_uc(self, boundary: RemovingDraftPurchaseOrderItemResponseBoundary,
                                            uow: InventoryUnitOfWork) -> RemoveDraftPurchaseOrderItemUC:
        return RemoveDraftPurchaseOrderItemUC(boundary, uow)


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

__all__ = [
    InventoryEventHandlerModule, InventoryInfrastructureModule
]
