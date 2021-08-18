#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from shop.domain.entities.shop_catalog import ShopCatalog


@dataclass(unsafe_hash=True)
class ShopCollection:
  title: str
  default: bool = False
  disabled: bool = False
  deleted: bool = False

  @property
  def catalog(self) -> 'ShopCatalog':
    return getattr(self, '_catalog')

  def __str__(self):
    return f'<ShopCollection #{self.collection_id} catalog="{self.catalog.title}">'

  def __eq__(self, other):
    if not other or not isinstance(other, ShopCollection):
      return False

    return self.title == other.title
