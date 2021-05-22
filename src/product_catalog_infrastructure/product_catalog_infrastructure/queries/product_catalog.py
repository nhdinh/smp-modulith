#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.engine.row import RowProxy

from auctions_infrastructure.queries.base import SqlQuery
from product_catalog.application.queries.product_catalog import GetAllProductsQuery, ProductDto
from product_catalog.application.queries.product_catalog import GetCatalogQuery, CatalogDto, GetAllCatalogsQuery, \
    PaginationDto
from product_catalog_infrastructure.adapter.catalog_db import catalog_table, product_table, collection_table, \
    brand_table


class SqlGetAllCatalogsQuery(GetAllCatalogsQuery, SqlQuery):
    def query(self, page: int, page_size: int) -> PaginationDto:
        total_rows = self._conn.scalar(select([func.count()]).select_from(product_table))

        # make joined table
        joined_table = catalog_table \
            .join(collection_table, onclause=(catalog_table.c.reference == collection_table.c.catalog_reference))

        # make query
        query = paginate(select(joined_table), page, page_size)

        return PaginationDto(
            data=[_row_to_catalog_dto(row) for row in self._conn.execute(joined_table.select())],
            current_page=page,
            page_size=page_size,
            total_rows=total_rows,
            total_pages=math.ceil(total_rows / page_size)
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
    def query(self, page: int, page_size: int) -> PaginationDto:
        total_rows = self._conn.scalar(select([func.count()]).select_from(product_table))

        joined_table = product_table \
            .join(catalog_table, catalog_table.c.reference == product_table.c.catalog_reference) \
            .join(collection_table, collection_table.c.reference == product_table.c.collection_reference) \
            .join(brand_table, brand_table.c.reference == product_table.c.brand_reference)

        query = select([
            product_table.c.product_id,
            product_table.c.reference,
            product_table.c.display_name,
            product_table.c.created_at,
            catalog_table.c.display_name.label('catalog_display_name'),
            collection_table.c.display_name.label('collection_display_name'),
            brand_table.c.display_name.label('brand_display_name'),
        ]) \
            .select_from(joined_table) \
            .select_from(catalog_table) \
            .select_from(collection_table) \
            .select_from(brand_table)

        query = paginate(query, page, page_size)

        return PaginationDto(
            items=[_row_to_product_dto(row) for row in self._conn.execute(query)],
            current_page=page,
            page_size=page_size,
            total_items=total_rows,
            total_pages=math.ceil(total_rows / page_size),
        )


def _row_to_catalog_dto(catalog_proxy: RowProxy) -> CatalogDto:
    return CatalogDto(
        reference=catalog_proxy.reference,
        display_name=catalog_proxy.display_name,
        disabled=catalog_proxy.disabled,
    )


def _row_to_product_dto(product_proxy: RowProxy) -> ProductDto:
    return ProductDto(
        product_id=product_proxy.product_id,
        reference=product_proxy.reference,
        display_name=product_proxy.display_name,
        catalog=product_proxy.catalog_display_name,
        brand=product_proxy.brand_display_name,
        collection=product_proxy.collection_display_name,
        created_at=product_proxy.created_at,
    )


def paginate(query, page: int, page_size: int):
    return query.limit(page_size).offset(page_size * (page - 1))
