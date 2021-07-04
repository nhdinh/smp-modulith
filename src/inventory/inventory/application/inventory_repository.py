#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Union

from foundation.entity import Entity
from foundation.events import EventMixin
from foundation.repository import AbstractRepository
from inventory.domain.entities.warehouse import Warehouse


class AbstractInventoryRepository(AbstractRepository):
    def _save(self, model: Union[EventMixin, Entity]):
        pass


class SqlAlchemyInventoryRepository(AbstractInventoryRepository):
    def _save(self, model: Warehouse) -> None:
        self._sess.add(model)

    def fetch_warehouse_of_owner(self, owner: str):
        return self._sess.query(Warehouse).where(Warehouse.warehouse_owner == owner).first()
