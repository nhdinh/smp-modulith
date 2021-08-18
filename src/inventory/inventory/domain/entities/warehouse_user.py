#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime

from inventory.domain.entities.value_objects import SystemUserId, SystemUserStatus, WarehouseUserType


@dataclass
class SystemUser:
  user_id: SystemUserId
  email: str
  mobile: str
  hashed_password: str
  confirmed_at: datetime
  status: SystemUserStatus

  def __hash__(self):
    return hash(self.email)


@dataclass(unsafe_hash=True)
class WarehouseUser:
  user_id: SystemUserId
  email: str
  warehouse_role: WarehouseUserType
