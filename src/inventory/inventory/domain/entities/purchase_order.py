#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import date
from typing import NewType, Set

from inventory.domain.entities.purchase_order_item import PurchaseOrderItem
from inventory.domain.entities.value_objects import PurchaseOrderStatus

PurchaseOrderId = NewType('PurchaseOrderId', tp=str)


@dataclass
class PurchaseOrder:
    purchase_order_id: PurchaseOrderId
    approved_date: date
    status: PurchaseOrderStatus

    items: Set[PurchaseOrderItem]

    def __hash__(self):
        return hash(self.purchase_order_id)
