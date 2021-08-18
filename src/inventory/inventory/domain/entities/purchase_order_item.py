#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from decimal import Decimal

from foundation.value_objects import Money
from foundation.value_objects.factories import get_money


@dataclass(unsafe_hash=True)
class PurchaseOrderItem:
  def __init__(
      self,
      product_title: str,
      product_sku: str,
      product_barcode: str,
      catalog_title: str,
      brand_name: str,
      brand_logo: str,
      unit: str,
      quantity: float,
      price: Money,
      tax: float,
      description: str
  ):
    self.product_title = product_title
    self.product_sku = product_sku
    self.product_barcode = product_barcode

    self.catalog_title = catalog_title

    self.brand_name = brand_name

    self.brand_logo = brand_logo

    self.unit = unit
    self.quantity = quantity
    self.price_amount = price.amount
    self.price_currency = price.currency.iso_code
    self.total_amount = self.price_amount * Decimal(self.quantity)
    self.tax = tax

    self.description = description

  @property
  def price(self) -> Money:
    return get_money(amount=self.price_amount, currency_str=self.price_currency)

#
# def __hash__(self):
#     return hash(self.purchase_order_item_id)
