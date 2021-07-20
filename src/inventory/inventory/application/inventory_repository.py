#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import Optional

from foundation.repository import AbstractRepository

from inventory.domain.entities.warehouse import Warehouse
from inventory.domain.entities.warehouse_user import WarehouseUser


class SqlAlchemyInventoryRepository(AbstractRepository):
    def get_warehouse_by_admin_id(self, user_id: str) -> Optional[Warehouse]:
        return self._sess.query(Warehouse) \
            .join(WarehouseUser, Warehouse._users).filter(WarehouseUser.user_id == user_id).first()


    def _save(self, warehouse: Warehouse) -> None:
        self._sess.add(warehouse)