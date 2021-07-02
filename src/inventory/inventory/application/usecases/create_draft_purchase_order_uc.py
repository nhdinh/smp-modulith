#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List

from foundation.value_objects.address import LocationAddressId
from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from inventory.application.usecases.inventory_uc_common import fetch_warehouse_by_owner_or_raise
from inventory.domain.entities.purchase_order import PurchaseOrderReference, DraftPurchaseOrder
from inventory.domain.entities.warehouse import Warehouse
from store.domain.entities.store_product import StoreProductId


@dataclass
class PurchaseOrderItemRequest:
    product_id: StoreProductId
    unit: str
    stock_quantity: int
    purchase_price: float
    description: str


@dataclass
class CreatingDraftPurchaseOrderRequest:
    current_user: str

    creator: str
    delivery_address: LocationAddressId
    note: str
    due_date: date
    status: str
    items: List[PurchaseOrderItemRequest] = field(default_factory=list)

    created_at: datetime = datetime.now()


@dataclass
class CreatingDraftPurchaseOrderResponse:
    reference: PurchaseOrderReference
    created_by: str
    created_at: datetime


class CreatingDraftPurchaseOrderResponseBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, response_dto: CreatingDraftPurchaseOrderResponse):
        raise NotImplementedError


class CreateDraftPurchaseOrderUC:
    def __init__(self, boundary: CreatingDraftPurchaseOrderResponseBoundary, uow: InventoryUnitOfWork):
        self._ob = boundary
        self._uow = uow

    def execute(self, dto: CreatingDraftPurchaseOrderRequest):
        with self._uow as uow:
            try:
                warehouse = fetch_warehouse_by_owner_or_raise(owner=dto.current_user, uow=uow)  # type: Warehouse

                po_data = dto
                draft_purchase_order = warehouse.create_draft_purchase_order(po_data)  # type:DraftPurchaseOrder

                response_dto = CreatingDraftPurchaseOrderResponse(
                    reference=draft_purchase_order.reference,
                    created_by=draft_purchase_order.creator,
                    created_at=draft_purchase_order.created_at
                )
                self._ob.present(response_dto=response_dto)
                uow.commit()
            except Exception as exc:
                raise exc
