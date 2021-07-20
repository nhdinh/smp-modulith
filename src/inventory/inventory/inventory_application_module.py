#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from inventory.application.usecases.approve_purchase_order_uc import (
    ApprovePurchaseOrderUC,
    ApprovingPurchaseOrderResponseBoundary,
)
from inventory.application.usecases.create_draft_purchase_order_uc import (
    CreateDraftPurchaseOrderUC,
    CreatingDraftPurchaseOrderResponseBoundary,
)
from inventory.application.usecases.remove_draft_purchase_order_item_uc import (
    RemoveDraftPurchaseOrderItemUC,
    RemovingDraftPurchaseOrderItemResponseBoundary,
)
from inventory.application.usecases.update_draft_purchase_order_uc import (
    UpdateDraftPurchaseOrderUC,
    UpdatingDraftPurchaseOrderResponseBoundary,
)


class InventoryApplicationModule(injector.Module):

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
