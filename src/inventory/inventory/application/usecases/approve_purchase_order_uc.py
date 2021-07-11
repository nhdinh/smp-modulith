#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
from datetime import date

from inventory.application.usecases.const import ExceptionMessages
from inventory.domain.entities.purchase_order_status import PurchaseOrderStatus
from inventory.domain.entities.warehouse import Warehouse

from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from inventory.application.usecases.inventory_uc_common import get_warehouse_by_owner_or_raise, \
    get_draft_purchase_order_from_warehouse_or_raise
from inventory.domain.entities.draft_purchase_order import DraftPurchaseOrderId


@dataclass
class ApprovingPurchaseOrderRequest:
    current_user: str
    draft_purchase_order_id: DraftPurchaseOrderId
    approved_at: date


@dataclass
class ApprovingPurchaseOrderResponse:
    status: bool


class ApprovingPurchaseOrderResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: ApprovingPurchaseOrderResponse):
        raise NotImplementedError


class ApprovePurchaseOrderUC:
    def __init__(self, boundary: ApprovingPurchaseOrderResponseBoundary, uow: InventoryUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: ApprovingPurchaseOrderRequest):
        with self._uow as uow:
            try:
                warehouse = get_warehouse_by_owner_or_raise(owner=dto.current_user, uow=uow)  # type: Warehouse

                # check the purchase orders with the latest date
                latest_date = warehouse.get_latest_purchase_order_date()
                if dto.approved_at < latest_date:
                    raise Exception(ExceptionMessages.APPROVE_DATE_CANNOT_BE_EARLIER_THAN_LATEST_DATE_IN_DATABASE)

                # if the date is good to approve, then select the draft purchase order
                draft_purchase_order = get_draft_purchase_order_from_warehouse_or_raise(
                    draft_purchase_order_id=dto.draft_purchase_order_id, warehouse=warehouse)

                # trying to get the draft purchase approved and copy the data into the (official) purchase order
                draft_purchase_order.approve()

                response = ApprovingPurchaseOrderResponse(status=True)
                self._ob.present(response)

                warehouse.version += 1

                uow.commit()
            except Exception as exc:
                raise exc
