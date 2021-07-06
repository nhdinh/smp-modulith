#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime, date
from typing import NewType, List, Tuple
from uuid import UUID

from foundation.entity import Entity
from foundation.events import EventMixin
from inventory.domain.entities.draft_purchase_order_item import DraftPurchaseOrderItem
from inventory.domain.entities.purchase_order_status import PurchaseOrderStatus
from store.domain.entities.store_address import StoreAddress
from store.domain.entities.store_supplier import StoreSupplier

DraftPurchaseOrderId = NewType('DraftPurchaseOrderId', tp=str)
PurchaseOrderId = NewType('PurchaseOrderId', tp=str)
PurchaseOrderReference = NewType('PurchaseOrderReference', tp=str)


class DraftPurchaseOrder(EventMixin, Entity):
    def __init__(
            self,
            purchase_order_id: DraftPurchaseOrderId,
            supplier: StoreSupplier,
            delivery_address: StoreAddress,
            note: str,
            due_date: date,
            creator: str,
            status: PurchaseOrderStatus = PurchaseOrderStatus.DRAFT,
            items: List[DraftPurchaseOrderItem] = None,
            version: int = 0,
    ):
        super(DraftPurchaseOrder, self).__init__()

        # check rules

        self.purchase_order_id = purchase_order_id
        self._supplier = supplier
        self._delivery_address = delivery_address
        self.note = note
        self.due_date = due_date
        self.creator = creator
        self.status = status

        # purchase order items
        self._items = items if items else set([])

        self.created_at: datetime = datetime.now()
        self.version: int = version

    @property
    def supplier(self):
        return self._supplier

    @property
    def delivery_address(self):
        return self._delivery_address

    @property
    def items(self):
        return self._items

    def add_or_merge_items(self, items: List[DraftPurchaseOrderItem]) -> Tuple[int, int]:
        """
        Merge items of this purchase Order with the list of input items

        :param items: List of PurchaseOrderItem
        :return: Numbers of (added, updated) items
        """
        try:
            added = 0
            updated = 0

            product_and_unit_pairs = [(i.product, i.unit) for i in self.items]

            while len(items):
                item = items.pop()

                if (item.product, item.unit) in product_and_unit_pairs:
                    updated += 1
                    child_item = next(i for i in self.items if i.product == item.product and i.unit == item.unit)
                    child_item.quantity += item.quantity
                else:
                    added += 1
                    self.items.add(item)

            return added, updated
        except Exception as exc:
            raise exc

    def remove_item(self, item: DraftPurchaseOrderItem):
        try:
            try:
                item_to_remove = next(
                    _item for _item in self._items if _item.product == item.product and _item.unit == item.unit)
                if item_to_remove:
                    self._items.remove(item_to_remove)
            except StopIteration:
                pass
        except Exception as exc:
            raise exc
