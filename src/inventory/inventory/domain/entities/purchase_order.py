#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from enum import Enum
from typing import NewType, List
from uuid import UUID

from foundation.events import EventMixin
from foundation.value_objects.address import LocationAddress
from inventory.domain.entities.purchase_order_item import PurchaseOrderItem
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_supplier import StoreSupplier


class PurchaseOrderStatus(Enum):
    DRAFT = 'DRAFT'
    APPROVED = 'APPROVED'
    DECLINED = 'DECLINED'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    COMPLETED_PARTLY = 'COMPLETED_PARTLY'
    FAILED = 'FAILED'


PurchaseOrderId = NewType('PurchaseOrderId', tp=UUID)
PurchaseOrderReference = NewType('PurchaseOrderReference', tp=str)


class PurchaseOrder(EventMixin):
    def __init__(
            self,
            purchase_order_id: PurchaseOrderId,
            reference: PurchaseOrderReference,
            delivery_address: LocationAddress,
            note: str,
            purchase_order_items: List[PurchaseOrderItem],
            supplier: StoreSupplier,
            due_date: datetime,
            creator: StoreOwner,
            version: int = 0,
    ):
        super(PurchaseOrder, self).__init__()

        self.purchase_order_id = purchase_order_id
        self.reference = reference
        self.delivery_address = delivery_address
        self.note = note

        self._items = purchase_order_items
        self.supplier = supplier
        self.due_date = due_date
        self.created_at: datetime = datetime.now()

        self.creator = creator
        self.approved_by = None

        self.status = PurchaseOrderStatus.DRAFT

        self.is_draft = True
        self.version: int = version

        # children
        self._items = []  # type: List[PurchaseOrderItem]

    @property
    def items(self):
        return self._items


class DraftPurchaseOrder(PurchaseOrder):
    pass


class SubmittedPurchaseOrder(PurchaseOrder):
    def __init__(self, approved_at: datetime):
        super(SubmittedPurchaseOrder, self).__init__()

        self.approved_at = approved_at
