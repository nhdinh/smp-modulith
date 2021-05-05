#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc

from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker, Session

from foundation.events import EventBus
from product_catalog.domain.entities.catalog import Catalog
from product_catalog.domain.value_objects import CatalogReference
from product_catalog.catalog_db import catalog_table


class AbstractCatalogRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, reference: CatalogReference) -> Catalog:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, catalog: Catalog) -> None:
        raise NotImplementedError


class SqlAlchemyCatalogRepository(AbstractCatalogRepository):
    def __init__(self, connection: Connection, event_bus: EventBus):
        self._conn = connection  # type:Connection
        self._event_bus = event_bus

    def get(self, reference: CatalogReference) -> Catalog:
        sessionfactory = sessionmaker(bind=self._conn.engine)
        session = sessionfactory()  # type:Session
        rows = session.query(Catalog).filter(Catalog.reference == reference).all()

        if not rows:
            raise Exception("Not found")

        return rows[0]

    def save(self, catalog: Catalog) -> None:
        pass
