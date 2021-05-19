#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import Optional

from sqlalchemy.orm import Session

from product_catalog.domain.entities.catalog import Catalog
from product_catalog.domain.value_objects import CatalogReference


class AbstractCatalogRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, reference: CatalogReference) -> Catalog:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, catalog: Catalog) -> None:
        raise NotImplementedError


class SqlAlchemyCatalogRepository(AbstractCatalogRepository):
    def __init__(self, session: Session):
        self._sess = session  # type:Session

    def get(self, reference: CatalogReference) -> Optional[Catalog]:
        """
        Get the catalog with specified reference string

        :param reference: reference string to find
        :return: the catalog if found, else return None
        :rtype: Optional[Catalog]
        """
        row = self._sess.query(Catalog).filter(Catalog.reference == reference).first()
        return row

    def get_default_catalog(self):
        row = self._sess.query(Catalog).filter(Catalog._reference == 'default_catalog').first()
        if not row:
            catalog = Catalog.create(reference='default_catalog', display_name='Default Catalog')
            self._sess.add(catalog)

            return catalog

        return row

    def save(self, catalog: Catalog) -> None:
        self._sess.add(catalog)
