#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Union

from foundation.entity import Entity
from foundation.events import EventMixin
from foundation.repository import AbstractRepository


class AbstractInventoryRepository(AbstractRepository):
    def _save(self, model: Union[EventMixin, Entity]):
        pass


class SqlAlchemyInventoryRepository(AbstractInventoryRepository):
    def _save(self, model: Union[EventMixin, Entity]) -> None:
        self._sess.add(model)
