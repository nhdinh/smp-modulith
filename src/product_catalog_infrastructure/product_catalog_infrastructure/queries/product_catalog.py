#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Optional, Tuple

from sqlalchemy.engine.row import RowProxy

from auctions_infrastructure.queries.base import SqlQuery
from product_catalog.application.queries.product_catalog import GetAllProductsQuery, ProductDto
from product_catalog.application.queries.product_catalog import GetCatalogQuery, CatalogDto, GetAllCatalogsQuery, \
    PaginationDto
from product_catalog_infrastructure.adapter.catalog_db import catalog_table, product_table, collection_table


class SqlGetAllCatalogsQuery(GetAllCatalogsQuery, SqlQuery):
    def query(self, page: int, page_size: int) -> Tuple[List[CatalogDto], PaginationDto]:
        joined_table = catalog_table \
            .join(collection_table, onclause=(catalog_table.c.reference == collection_table.c.catalog_reference))

        return [
                   _row_to_catalog_dto(row) for row in
                   self._conn.execute(joined_table.select())
               ], \
               PaginationDto(
                   current_page=page,
                   page_size=page_size,
                   total_pages=0
               )


class SqlGetCatalogQuery(GetCatalogQuery, SqlQuery):
    def query(self, param: str) -> Optional[CatalogDto]:
        try:
            return next(
                _row_to_catalog_dto(row) for row in
                self._conn.execute(catalog_table.select().where(catalog_table.c.reference == param))
            )
        except StopIteration:
            return None
        except Exception as exc:
            raise exc


class SqlGetAllProductsQuery(GetAllProductsQuery, SqlQuery):
    def query(self, page: int, page_size: int) -> Tuple[List[ProductDto], PaginationDto]:
        join = product_table \
            .join(catalog_table, onclause=(catalog_table.c.reference == product_table.c.catalog_reference)) \
            .join(collection_table, onclause=(collection_table.c.reference == product_table.c.collection_reference))

        return [_row_to_product_dto(row) for row in self._conn.execute(join.select())], \
               PaginationDto(
                   current_page=page,
                   page_size=page_size,
                   total_pages=self._conn.execute(f'select count(reference) from {product_table.name}').scalar()
               )


def _row_to_catalog_dto(catalog_proxy: RowProxy) -> CatalogDto:
    return CatalogDto(
        reference=catalog_proxy.reference,
        display_name=catalog_proxy.display_name,
        disabled=catalog_proxy.disabled,
    )


def _row_to_product_dto(product_proxy: RowProxy) -> ProductDto:
    return ProductDto(
        reference=product_proxy.reference,
        display_name=product_proxy.display_name,
        catalog=product_proxy.display_name_1,
        collection=product_proxy.display_name_2,
    )
