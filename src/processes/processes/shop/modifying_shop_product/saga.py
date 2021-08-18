#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from foundation.method_dispatch import method_dispatch
from inventory.inventory_handler_facade import InventoryHandlerFacade
from processes.value_objects import ProcessId
from shop.application.shop_handler_facade import ShopHandlerFacade
from shop.domain.events import ShopProductCreatedEvent, ShopProductUpdatedEvent


class State(Enum):
  PROCESS_STARTED = "PROCESS_STARTED"
  FINISHED = "FINISHED"


@dataclass
class CreatingShopProductData:
  process_id: ProcessId
  state: Optional[State] = None
  timeout_at: Optional[datetime] = None

  shop_id: Optional[str] = None
  product_id: Optional[str] = None


class ShopCreatingNewProduct:
  def __init__(self,
               shop_facade: ShopHandlerFacade,
               inventory_facade: InventoryHandlerFacade):
    self._shop = shop_facade
    self._inventory = inventory_facade

  @method_dispatch
  def handle(self, event: Any, data: CreatingShopProductData):
    raise Exception(f"Unhandled event {event}")

  @handle.register(ShopProductCreatedEvent)  # type:ignore
  def handle_shop_product_created(self, event: ShopProductCreatedEvent, data: CreatingShopProductData) -> None:
    assert data.state is None

    self._shop.update_shop_product_cache(product_id=event.product_id, shop_id=event.shop_id)
    self._inventory.update_first_stocking(
      product_id=event.product_id,
      shop_id=event.shop_id,
      units=[],
      first_stocking=[]
    )

    data.product_id = event.product_id
    data.shop_id = event.shop_id
    data.state = State.FINISHED

  @handle.register(ShopProductUpdatedEvent)  # type:ignore
  def handle_shop_product_updated(self, event: ShopProductUpdatedEvent, data: CreatingShopProductData) -> None:
    assert data.state is None

    self._shop.update_shop_product_cache(product_id=event.product_id, shop_id=event.shop_id)

    data.product_id = event.product_id
    data.shop_id = event.shop_id
    data.state = State.FINISHED
