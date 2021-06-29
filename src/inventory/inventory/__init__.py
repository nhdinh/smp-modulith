#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.orm import sessionmaker
from typing import Type

from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from sqlalchemy.engine import Connection

from foundation.events import EventBus, AsyncEventHandlerProvider, AsyncHandler
from inventory.application.usecases.approve_purchase_order_uc import ApprovePurchaseOrderUC, \
    ApprovingPurchaseOrderResponseBoundary
from inventory.application.usecases.create_draft_purchase_order_uc import CreatingDraftPurchaseOrderResponseBoundary, \
    CreateDraftPurchaseOrderUC
from inventory.application.usecases.update_draft_purchase_order_uc import UpdatingDraftPurchaseOrderResponseBoundary, \
    UpdateDraftPurchaseOrderUC
from inventory.inventory_handler_facade import InventoryHandlerFacade, StoreProductCreatedEventHandler
from store.domain.events.store_product_created_event import StoreProductCreatedEvent


class InventoryModule(injector.Module):
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
    def facade(self, connection: Connection) -> InventoryHandlerFacade:
        return InventoryHandlerFacade(connection=connection)

    def async_bind(self, binder: injector.Binder, event: Type, handler: Type) -> None:
        # shorthand for multi-bind
        binder.multibind(AsyncHandler[event], to=AsyncEventHandlerProvider(handler))

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[StoreProductCreatedEvent],
                         to=AsyncEventHandlerProvider(StoreProductCreatedEventHandler))


class InventoryInfrastructureModule(injector.Module):
    @injector.provider
    def get_uow(self, conn: Connection, event_bus: EventBus) -> InventoryUnitOfWork:
        sessfactory = sessionmaker(bind=conn)
        return InventoryUnitOfWork(sessionfactory=sessfactory, event_bus=event_bus)


__all__ = [
    InventoryModule, InventoryInfrastructureModule
]
