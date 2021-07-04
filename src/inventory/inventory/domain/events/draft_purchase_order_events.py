#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from foundation import Event
from inventory.domain.entities.purchase_order import DraftPurchaseOrderId


@dataclass
class DraftPurchaseOrderCreatedEvent(Event):
    purchase_order_id: DraftPurchaseOrderId
    creator: str


@dataclass
class DraftPurchasedOrderUpdatedEvent(Event):
    purchase_order_id: DraftPurchaseOrderId
    updated_by: str
