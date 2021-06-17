#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import select, and_
from sqlalchemy.engine.row import RowProxy

from store.adapter.queries.query_common import sql_fetch_store_by_owner, sql_fetch_collection_by_reference, \
    sql_count_products_from_collection

from db_infrastructure import SqlQuery
from store.adapter.store_db import store_settings_table, store_table, store_owner_table, store_product_table, \
    store_collection_table, store_brand_table, store_catalog_table
from store.application.queries.store_queries import FetchStoreProductsFromCollectionQuery, StoreProductResponseDto
from store.application.store_queries import FetchStoreSettingsQuery, StoreSettingResponseDto, \
    CountStoreOwnerByEmailQuery, StoreInfoResponseDto
from store.domain.entities.value_objects import StoreCollectionReference, StoreCatalogReference
from web_app.serialization.dto import PaginationOutputDto, AuthorizedPaginationInputDto, paginate_response_factory


def _row_to_store_settings_dto(row: RowProxy) -> StoreSettingResponseDto:
    return StoreSettingResponseDto(
        name=row.setting_key,
        value=row.setting_value,
        type=row.setting_type,
    )


def _row_to_store_info_dto(store_row_proxy: RowProxy) -> StoreInfoResponseDto:
    return StoreInfoResponseDto(
        store_id=store_row_proxy.store_id,
        store_name=store_row_proxy.name,
        settings=[]
    )


class SqlFetchStoreSettingsQuery(FetchStoreSettingsQuery, SqlQuery):
    def query(self, store_of: str) -> StoreInfoResponseDto:
        store_query = select([
            store_table.c.store_id,
            store_table.c.name,
        ]) \
            .select_from(store_table.join(store_owner_table, onclause=(store_table.c.owner == store_owner_table.c.id))) \
            .select_from(store_table) \
            .where(store_owner_table.c.email == store_of)

        store_row_proxy = self._conn.execute(store_query).first()
        if not store_row_proxy:
            return None

        # make StoreInfoResponseDto
        return_dto = _row_to_store_info_dto(store_row_proxy)

        query = select([
            store_settings_table.c.setting_key,
            store_settings_table.c.setting_value,
            store_settings_table.c.setting_type,
        ]) \
            .select_from(store_settings_table) \
            .where(store_settings_table.c.store_id == return_dto.store_id)

        rows = self._conn.execute(query).all()

        # build settings[]
        for row in rows:
            return_dto.settings.append(_row_to_store_settings_dto(row))

        # return the dto
        return return_dto


class SqlCountStoreOwnerByEmailQuery(CountStoreOwnerByEmailQuery, SqlQuery):
    def query(self, email: str) -> int:
        raise NotImplementedError


def _row_to_product_dto(product_proxy: RowProxy) -> StoreProductResponseDto:
    return StoreProductResponseDto(
        product_id=product_proxy.product_id,
        reference=product_proxy.reference,
        display_name=product_proxy.display_name,
        catalog=product_proxy.catalog_display_name,
        brand=product_proxy.brand_display_name,
        collection=product_proxy.collection_display_name,
        created_at=product_proxy.created_at,
    )


class SqlFetchStoreProductsFromCollectionQuery(FetchStoreProductsFromCollectionQuery, SqlQuery):
    def query(
            self,
            collection_reference: StoreCollectionReference,
            catalog_reference: StoreCatalogReference,
            dto: AuthorizedPaginationInputDto
    ) -> PaginationOutputDto[StoreProductResponseDto]:
        try:
            current_page = dto.page if dto.page else 1

            # get store_id and collection_id
            store_id = sql_fetch_store_by_owner(store_owner=dto.current_user, conn=self._conn)
            collection_id = sql_fetch_collection_by_reference(collection_reference=collection_reference,
                                                              catalog_reference=catalog_reference, store_id=store_id,
                                                              conn=self._conn)

            # count products in collection
            product_in_collection_count = sql_count_products_from_collection(collection_reference=collection_reference,
                                                                             catalog_reference=catalog_reference,
                                                                             store_id=store_id,
                                                                             conn=self._conn)

            q = select([
                store_product_table.c.product_id,
                store_product_table.c.reference,
                store_product_table.c.display_name,

                store_collection_table.c.display_name.label('collection_display_name'),
                store_catalog_table.c.display_name.label('catalog_display_name'),
                store_brand_table.c.display_name.label('brand_display_name'),
                store_product_table.c.created_at,
            ]) \
                .select_from(store_product_table) \
                .select_from(store_catalog_table) \
                .select_from(store_collection_table) \
                .select_from(store_brand_table) \
                .join(store_collection_table,
                      onclause=(store_product_table.c.collection_id == store_collection_table.c.collection_id)) \
                .join(store_catalog_table,
                      onclause=(store_collection_table.c.catalog_id == store_catalog_table.c.catalog_id)) \
                .where(store_catalog_table.c.store_id == store_id) \
                .where(store_collection_table.c.reference == collection_reference) \
                .where(store_catalog_table.c.reference == catalog_reference) \
                .limit(dto.page_size).offset((current_page - 1) * dto.page_size)

            products = self._conn.execute(q).all()

            return paginate_response_factory(
                current_page=current_page,
                page_size=dto.page_size,
                total_items=product_in_collection_count,
                items=[
                    _row_to_product_dto(row) for row in products
                ]
            )

        except Exception as exc:
            raise exc
