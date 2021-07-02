#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import NewType
from uuid import UUID

from foundation.events import EventMixin
from inventory.domain.entities.purchase_order import PurchaseOrderReference, DraftPurchaseOrder

WarehouseId = NewType('WarehouseId', tp=UUID)


class Warehouse(EventMixin):
    def __init__(self):
        self.disabled = None

    def create_draft_purchase_order(
            self,
            reference: PurchaseOrderReference,
    ) -> DraftPurchaseOrder:
        pass
