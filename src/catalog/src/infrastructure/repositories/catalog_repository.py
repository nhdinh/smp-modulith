#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc

from sqlalchemy.engine import Connection

from foundation.events import EventBus
from src.domain.entities.catalog import Catalog
from src.domain.value_objects import CatalogReference


class AbstractCatalogRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, reference: CatalogReference) -> Catalog:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, catalog: Catalog) -> None:
        raise NotImplementedError


class SqlAlchemyCatalogRepository(AbstractCatalogRepository):
    def __init__(self, connection: Connection, event_bus: EventBus):
        self._conn = connection
        self._event_bus = event_bus

    def get(self, reference: CatalogReference) -> Catalog:
        pass

    def save(self, catalog: Catalog) -> None:
        pass
