#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from typing import List, Optional

from sqlalchemy.engine.row import RowProxy

from auctions_infrastructure.queries.base import SqlQuery
from product_catalog.application.queries.product_catalog import GetCatalogQuery, CatalogDto, GetAllCatalogsQuery
from product_catalog_infrastructure import catalog_table


class SqlGetAllCatalogsQuery(GetAllCatalogsQuery, SqlQuery):
    def query(self) -> List[CatalogDto]:
        return [
            _row_to_dto(row) for row in self._conn.execute(catalog_table.select())
        ]


class SqlGetCatalogQuery(GetCatalogQuery, SqlQuery):
    def query(self, reference: str) -> Optional[CatalogDto]:
        try:
            return next(
                _row_to_dto(row) for row in
                self._conn.execute(catalog_table.select().where(catalog_table.c.reference == reference))
            )
        except StopIteration:
            return None


def _row_to_dto(catalog_proxy: RowProxy) -> CatalogDto:
    return CatalogDto(
        id=catalog_proxy.id,
        reference=catalog_proxy.reference,
        display_name=catalog_proxy.display_name,
        disabled=catalog_proxy.disabled,
    )
