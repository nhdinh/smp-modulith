#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, List

from sqlalchemy import func, select
from sqlalchemy.engine.row import RowProxy

from db_infrastructure import SqlQuery
from db_infrastructure.base import paginate
from product_catalog.adapter.catalog_db import catalog_table, product_table, collection_table, \
    brand_table
from product_catalog.application.queries.product_catalog import FetchAllProductsQuery, ProductDto, FetchProductQuery, \
    CollectionDto, BrandDto, FetchAllBrandsQuery
from product_catalog.application.queries.product_catalog import FetchCatalogQuery, CatalogDto, FetchAllCatalogsQuery
from web_app.serialization.dto import PaginationOutputDto, paginate_response_factory


class SqlFetchAllCatalogsQuery(FetchAllCatalogsQuery, SqlQuery):
    def query(self, select_active_only: bool = True) -> List[CatalogDto]:
        # make query
        query_table = catalog_table.join(collection_table, onclause=(
                catalog_table.c.reference == collection_table.c.catalog_reference), isouter=True)

        query = select([
            catalog_table.c.reference,
            catalog_table.c.display_name,
            catalog_table.c.disabled,
            catalog_table.c.system,
            collection_table.c.reference.label('collection_reference'),
            collection_table.c.display_name.label('collection_display_name'),
            collection_table.c.default.label('collection_default'),
        ]) \
            .select_from(query_table) \
            .select_from(catalog_table) \
            .select_from(collection_table)

        if select_active_only:
            query = query.where(catalog_table.c.disabled == False)
        result = self._conn.execute(query)

        ret = dict()
        for row in result:
            catalog_dto = _row_to_catalog_dto(row)

            if catalog_dto.reference not in ret.keys():
                ret[catalog_dto.reference] = catalog_dto

            if not hasattr(ret[catalog_dto.reference], 'collections'):
                setattr(ret[catalog_dto.reference], 'collections', [])

            # fetch collection from RowProxy and make sure its content is not Null in both reference and display_name
            _collection = _row_to_collection_dto(row)
            if _collection.collection_reference and _collection.collection_display_name:
                ret[catalog_dto.reference].collections.append(_collection)

        return list(ret.values())


class SqlFetchCatalogQuery(FetchCatalogQuery, SqlQuery):
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


class SqlFetchProductQuery(FetchProductQuery, SqlQuery):
    def query(self, product_query: str) -> Optional[ProductDto]:
        try:
            query = joined_product_table_query()
            result = self._conn.execute(query.where(product_table.c.reference == product_query)).first()

            if result:
                return _row_to_product_dto(result)
            else:
                return {}
        except Exception as exc:
            raise exc


class SqlFetchAllProductsQuery(FetchAllProductsQuery, SqlQuery):
    def query(self, page: int, page_size: int) -> PaginationOutputDto[ProductDto]:
        total_rows = self._conn.scalar(select([func.count()]).select_from(product_table))

        query = joined_product_table_query()

        query = paginate(query, page, page_size)

        return paginate_response_factory(
            current_page=page,
            page_size=page_size,
            total_items=total_rows,
            items=[_row_to_product_dto(row) for row in self._conn.execute(query)],
        )


class SqlFetchAllBrandsQuery(FetchAllBrandsQuery, SqlQuery):
    def query(self) -> List[BrandDto]:
        return [_row_to_brand_dto(r) for r in self._conn.execute(brand_table.select())]


def joined_product_table_query():
    joined_table = product_table \
        .join(collection_table, collection_table.c.reference == product_table.c.collection_reference) \
        .join(catalog_table, catalog_table.c.reference == collection_table.c.catalog_reference) \
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

    return query


def _row_to_catalog_dto(catalog_proxy: RowProxy) -> CatalogDto:
    return CatalogDto(
        reference=catalog_proxy.reference,
        display_name=catalog_proxy.display_name,
        disabled=catalog_proxy.disabled,
        collections=[],
        system=catalog_proxy.system,
    )


def _row_to_collection_dto(collection_proxy: RowProxy) -> CollectionDto:
    return CollectionDto(
        collection_reference=collection_proxy.collection_reference,
        collection_display_name=collection_proxy.collection_display_name,
        collection_default=collection_proxy.collection_default,
    )


def _row_to_brand_dto(brand_proxy: RowProxy) -> BrandDto:
    return BrandDto(
        brand_reference=brand_proxy.reference,
        brand_display_name=brand_proxy.display_name,
        brand_logo=brand_proxy.logo if hasattr(brand_proxy, 'logo') else ''
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
