#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import NewType, List
from uuid import UUID

from inventory.domain.entities.purchase_order_item import PurchaseOrderItem

PurchaseOrderId = NewType('PurchaseOrderId', tp=UUID)
PurchaseOrderReference = NewType('PurchaseOrderReference', tp=str)


class PurchaseOrder:
    def __init__(
            self,
            po_id: PurchaseOrderId,
            reference: PurchaseOrderReference,
            note: str,
            creator: str,
            version: int = 0
    ):
        self.po_id = po_id
        self.reference = reference
        self.note = note

        self.creator = creator
        self.created_at: datetime = datetime.now()

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
