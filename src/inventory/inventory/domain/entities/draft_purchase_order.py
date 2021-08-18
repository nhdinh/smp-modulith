#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import date, datetime
from typing import List, Tuple

from dateutil.utils import today

from foundation import Entity
from foundation import EventMixin
from inventory.adapter.id_generators import generate_purchase_order_id
from inventory.domain.entities.draft_purchase_order_item import DraftPurchaseOrderItem
from inventory.domain.entities.purchase_order import PurchaseOrder
from inventory.domain.entities.purchase_order_item import PurchaseOrderItem
from inventory.domain.entities.value_objects import DraftPurchaseOrderId, PurchaseOrderStatus
from inventory.domain.rules.draft_purchase_order_must_be_unconfirmed_status import (
  DraftPurchaseOrderMustBeUnconfirmedStatusRule,
)


class DraftPurchaseOrder(EventMixin, Entity):
  def __init__(
      self,
      purchase_order_id: DraftPurchaseOrderId,
      supplier: 'ShopSupplier',
      delivery_address: 'ShopAddress',
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

    # approved version
    self._approved_purchase_order = None

    # warehouse backref
    self._warehouse = None

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

  @property
  def approved_purchase_order(self):
    if self.status == PurchaseOrderStatus.APPROVED:
      return self._approved_purchase_order

    return None

  @approved_purchase_order.setter
  def approved_purchase_order(self, value: PurchaseOrder):
    if isinstance(value, PurchaseOrder):
      self._approved_purchase_order = value
      self.status = PurchaseOrderStatus.APPROVED
      self._approved_purchase_order._warehouse = self._warehouse

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

  def approve(self):
    approve_date = today()

    purchase_order = self.make_purchase_order(approve_date=approve_date)

    # update self
    self.status = PurchaseOrderStatus.APPROVED
    self.approved_purchase_order = purchase_order

    return purchase_order.purchase_order_id

  def make_purchase_order(self, approve_date: date):
    self.check_rule(DraftPurchaseOrderMustBeUnconfirmedStatusRule(self.status))

    purchase_order = PurchaseOrder(
      purchase_order_id=generate_purchase_order_id(),
      approved_date=approve_date,
      status=PurchaseOrderStatus.PROCESSING,
      items=set()
    )

    for item in self._items:
      purchase_order_item = self._make_purchase_order_item(item)
      purchase_order.items.add(purchase_order_item)

    return purchase_order

  def _make_purchase_order_item(self, item: DraftPurchaseOrderItem) -> PurchaseOrderItem:
    """
    Convert the draft purchase order item (with all referenced data) into valued PurchaseOrderItem. The referenced
    data will be copied and set hardly in the database

    :param item: return an instance of the PurchaseOrderItem
    """
    price_tuple = item.product.get_price(by_supplier=self._supplier, by_unit=item.unit)
    return PurchaseOrderItem(
      product_title=item.product.title,
      product_sku=item.product.sku,
      product_barcode=item.product.barcode,
      catalog_title=item.product.catalog.title,
      brand_name=item.product.brand.name if item.product.brand else '',
      brand_logo=item.product.brand.logo if item.product.brand else '',
      unit=item.unit.unit_name,
      quantity=item.quantity,
      price=price_tuple[0],
      tax=price_tuple[1],
      description=item.description
    )
