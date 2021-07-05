#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Union, TYPE_CHECKING, Optional

from foundation.value_objects.address import LocationAddressId
from inventory.application.services.inventory_unit_of_work import InventoryUnitOfWork
from inventory.application.usecases.inventory_uc_common import fetch_warehouse_by_owner_or_raise
from inventory.domain.entities.purchase_order import DraftPurchaseOrder
from inventory.domain.entities.purchase_order_status import PurchaseOrderStatus
from store.domain.entities.store_supplier import StoreSupplierId

if TYPE_CHECKING:
    from inventory.domain.entities.warehouse import Warehouse
from store.domain.entities.store_product import StoreProductId


@dataclass
class PurchaseOrderItemRequest:
    product_id: StoreProductId
    unit_name: str
    quantity: int
    description: str


@dataclass
class CreatingDraftPurchaseOrderRequest:
    current_user: str
    creator: str

    supplier_id_or_name: Union[StoreSupplierId, str]

    delivery_address: LocationAddressId
    note: str
    due_date: date
    status: PurchaseOrderStatus = PurchaseOrderStatus.DRAFT
    items: List[PurchaseOrderItemRequest] = field(default_factory=list)

    created_at: datetime = datetime.now()


@dataclass
class CreatingDraftPurchaseOrderResponse:
    status: bool


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

                po_data = dict()
                po_data['supplier_id_or_name'] = dto.supplier_id_or_name
                po_data['delivery_address'] = dto.delivery_address
                po_data['note'] = dto.note
                po_data['due_date'] = dto.due_date
                po_data['creator'] = dto.current_user
                po_data['items'] = []

                if dto.items:
                    for item in dto.items:
                        po_item_data = dict()
                        po_item_data['product_id'] = item.product_id
                        po_item_data['unit'] = item.unit_name
                        po_item_data['quantity'] = item.quantity
                        po_item_data['description'] = item.description

                        po_data['items'].append(po_item_data)

                # create draft purchase order
                draft_purchase_order = warehouse.create_draft_purchase_order(**po_data)  # type:DraftPurchaseOrder

                response_dto = CreatingDraftPurchaseOrderResponse(status=True)
                self._ob.present(response_dto=response_dto)
                uow.commit()
            except Exception as exc:
                raise exc
