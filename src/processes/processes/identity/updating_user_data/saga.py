#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from foundation.method_dispatch import method_dispatch
from identity.domain.events import UserDataEmitEvent
from inventory.inventory_handler_facade import InventoryHandlerFacade
from processes.value_objects import ProcessId
from shop.application.shop_handler_facade import ShopHandlerFacade


class State(Enum):
  STARTED = 'STARTED'
  FINISHED = 'FINISHED'


@dataclass
class UpdatedUserData:
  process_id: ProcessId
  state: Optional[State] = None


class UpdatingUserData:
  def __init__(self,
               shop_facade: ShopHandlerFacade,
               inventory_facade: InventoryHandlerFacade):
    self._shop = shop_facade
    self._inventory = inventory_facade

  @method_dispatch
  def handle(self, event: Any, data: UpdatedUserData):
    raise Exception(f"Unhandled event {event}")

  @handle.register(UserDataEmitEvent)  # type:ignore
  def handle_updating_user_data(self, event: UserDataEmitEvent, data: UpdatedUserData) -> None:
    """
    Update the user's data when `Identity` service emit an `UserDataEmitEvent`

    :param event: instance of `UserDataEmitEvent`
    """
    assert data.state is State.STARTED

    self._shop.update_shop_user_data(user_id=event.user_id, email=event.email, mobile=event.mobile)
    self._inventory.update_warehouse_user_data(user_id=event.user_id, email=event.email)
    data.state = State.FINISHED
