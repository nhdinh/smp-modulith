#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import select, and_

from db_infrastructure import SqlQuery
from store.adapter.queries.query_common import sql_get_store_id_by_owner, \
    sql_count_products_in_collection, sql_get_catalog_id_by_reference, sql_count_collections_in_catalog, \
    sql_count_catalogs_in_store
from store.adapter.queries.query_helpers import _row_to_store_settings_dto, _row_to_store_info_dto, \
    _row_to_product_short_dto, \
    _row_to_catalog_dto, _row_to_collection_dto, _row_to_product_dto
from store.application.queries.store_queries import FetchStoreProductsFromCollectionQuery, StoreProductShortResponseDto, \
    FetchStoreCollectionsQuery, FetchStoreCatalogsQuery, StoreCatalogResponseDto, FetchStoreProductQuery, \
    StoreProductResponseDto, FetchStoreProductByIdQuery
from store.application.store_queries import FetchStoreSettingsQuery, CountStoreOwnerByEmailQuery, StoreInfoResponseDto
from store.application.usecases.const import ExceptionMessages
from store.domain.entities.setting import Setting
from store.domain.entities.store import Store
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_product import StoreProduct
from store.domain.entities.store_product_brand import StoreProductBrand
from store.domain.entities.store_product_tag import StoreProductTag
from store.domain.entities.store_unit import StoreProductUnit
from store.domain.entities.value_objects import StoreCollectionReference, StoreCatalogReference, StoreProductReference, \
    StoreProductId, StoreId
from web_app.serialization.dto import PaginationOutputDto, AuthorizedPaginationInputDto, paginate_response_factory


class SqlFetchStoreSettingsQuery(FetchStoreSettingsQuery, SqlQuery):
    def query(self, store_of: str) -> StoreInfoResponseDto:
        store_query = select(Store) \
            .join(StoreOwner).where(StoreOwner.email == store_of)

        store_row_proxy = self._conn.execute(store_query).first()
        if not store_row_proxy:
            raise Exception(ExceptionMessages.STORE_NOT_FOUND)

        # make StoreInfoResponseDto
        return_dto = _row_to_store_info_dto(store_row_proxy)

        query = select(Setting) \
            .join(Store) \
            .where(Store.store_id == return_dto.store_id)

        rows = self._conn.execute(query).all()

        # build settings[]
        for row in rows:
            return_dto.settings.append(_row_to_store_settings_dto(row))

        # return the dto
        return return_dto


class SqlCountStoreOwnerByEmailQuery(CountStoreOwnerByEmailQuery, SqlQuery):
    def query(self, email: str) -> int:
        raise NotImplementedError


class SqlFetchStoreProductsFromCollectionQuery(FetchStoreProductsFromCollectionQuery, SqlQuery):
    def query(
            self,
            collection_reference: StoreCollectionReference,
            catalog_reference: StoreCatalogReference,
            dto: AuthorizedPaginationInputDto
    ) -> PaginationOutputDto[StoreProductShortResponseDto]:
        try:
            current_page = dto.page if dto.page else 1

            # get store_id and collection_id
            store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)

            # count products in collection
            product_in_collection_count = sql_count_products_in_collection(collection_reference=collection_reference,
                                                                           catalog_reference=catalog_reference,
                                                                           store_id=store_id,
                                                                           conn=self._conn)

            fetch_products_query = select([
                StoreProduct,
                StoreCollection.display_name.label('collection_display_name'),
                StoreCatalog.display_name.label('catalog_display_name'),
                StoreProductBrand.display_name.label('brand_display_name'),
            ]) \
                .join(StoreCollection, StoreProduct.collection_id == StoreCollection.collection_id) \
                .join(StoreCatalog, StoreProduct.catalog_id == StoreCatalog.catalog_id) \
                .join(Store, StoreProduct.store_id == Store.store_id) \
                .join(StoreProductBrand, and_(StoreProduct.brand_reference == StoreProductBrand.reference,
                                              Store.store_id == StoreProductBrand.store_id), isouter=True) \
                .where(and_(StoreCollection.reference == collection_reference,
                            StoreCatalog.reference == catalog_reference,
                            Store.store_id == store_id
                            )) \
                .limit(dto.page_size).offset((current_page - 1) * dto.page_size)

            products = self._conn.execute(fetch_products_query).all()

            return paginate_response_factory(
                current_page=current_page,
                page_size=dto.page_size,
                total_items=product_in_collection_count,
                items=[
                    _row_to_product_short_dto(row) for row in products
                ]
            )
        except Exception as exc:
            raise exc


class SqlFetchStoreCatalogsQuery(FetchStoreCatalogsQuery, SqlQuery):
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreCatalogResponseDto]:
        current_page = dto.page if dto.page > 0 else 1

        store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)

        # count number of catalogs of this store
        catalog_count = sql_count_catalogs_in_store(store_id=store_id, conn=self._conn)

        # get all catalogs limit by page and offset
        get_all_catalogs_query = select(StoreCatalog).join(Store) \
            .where(Store.store_id == store_id) \
            .limit(dto.page_size).offset((current_page - 1) * dto.page_size)

        try:
            catalogs = self._conn.execute(get_all_catalogs_query).all()
            if not catalogs:
                # return None
                return paginate_response_factory(
                    current_page=dto.page,
                    page_size=dto.page_size,
                    total_items=catalog_count,
                    items=[]
                )

            # else, continue to load collection
            catalog_indices = set()
            for catalog in catalogs:
                catalog_indices.add(catalog.catalog_id)

            # get all collection with catalog_id in the list of catalog_indices
            collection_query = select(StoreCollection).join(StoreCatalog).join(Store).where(
                StoreCatalog.catalog_id.in_(list(catalog_indices))) \
                .where(Store.store_id == store_id)

            collections = self._conn.execute(collection_query).all()

            return paginate_response_factory(
                current_page=dto.page,
                page_size=dto.page_size,
                total_items=catalog_count,
                items=[
                    _row_to_catalog_dto(row, collections=[c for c in collections if c.catalog_id == row.catalog_id])
                    for row in catalogs]
            )
        except Exception as exc:
            raise exc


class SqlFetchStoreCollectionsQuery(FetchStoreCollectionsQuery, SqlQuery):
    def query(self, catalog_reference: StoreCatalogReference, dto: AuthorizedPaginationInputDto):
        try:
            current_page = dto.page if dto.page else 1

            store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)
            catalog_id = sql_get_catalog_id_by_reference(catalog_reference=catalog_reference, store_id=store_id,
                                                         conn=self._conn)
            collection_count = sql_count_collections_in_catalog(store_id=store_id, catalog_id=catalog_id,
                                                                conn=self._conn)

            collection_query = select(StoreCollection).join(StoreCatalog).join(Store) \
                .where(and_(Store.store_id == store_id, StoreCatalog.catalog_id == catalog_id))

            collections = self._conn.execute(collection_query).all()
            return paginate_response_factory(
                current_page=current_page,
                page_size=dto.page_size,
                total_items=collection_count,
                items=[
                    _row_to_collection_dto(row) for row in collections
                ]
            )
        except Exception as exc:
            raise exc


def fetch_store_product_query_factory(store_id: StoreId):
    query = select([
        StoreProduct,
        StoreCatalog.reference.label('catalog_reference'),
        StoreCatalog.display_name.label('catalog_display_name'),

        StoreCollection.reference.label('collection_reference'),
        StoreCollection.display_name.label('collection_display_name'),

        StoreProductBrand.display_name.label('brand_display_name'),

        StoreProductUnit
    ]) \
        .join(StoreCollection, StoreProduct.collection_id == StoreCollection.collection_id) \
        .join(StoreCatalog, StoreProduct.catalog_id == StoreCatalog.catalog_id) \
        .join(Store, StoreProduct.store_id == StoreCatalog.store_id) \
        .join(StoreProductBrand, onclause=(StoreProduct.brand_reference == StoreProductBrand.reference), isouter=True) \
        .join(StoreProductUnit, isouter=True) \
        .where(Store.store_id == store_id)

    return query


class SqlFetchStoreProductQuery(FetchStoreProductQuery, SqlQuery):
    def query(self,
              owner_email: str,
              catalog_reference: StoreCatalogReference,
              collection_reference: StoreCollectionReference,
              product_reference: StoreProductReference
              ) -> StoreProductResponseDto:
        try:
            store_id = sql_get_store_id_by_owner(store_owner=owner_email, conn=self._conn)

            query = fetch_store_product_query_factory(store_id=store_id)
            query = query.where(
                and_(StoreCatalog.reference == catalog_reference,
                     StoreCollection.reference == collection_reference,
                     StoreProduct.reference == product_reference))

            product = self._conn.execute(query).first()
            return product
        except Exception as exc:
            raise exc


class SqlFetchStoreProductByIdQuery(FetchStoreProductByIdQuery, SqlQuery):
    def query(self,
              owner_email: str,
              product_id: StoreProductId):
        try:
            store_id = sql_get_store_id_by_owner(store_owner=owner_email, conn=self._conn)
            query = fetch_store_product_query_factory(store_id=store_id)
            query = query.where(StoreProduct.product_id == product_id)

            product = self._conn.execute(query).first()

            fetch_units_query = select(StoreProductUnit) \
                .join(StoreProduct) \
                .where(StoreProduct.product_id == product_id)
            units = self._conn.execute(fetch_units_query).all()

            fetch_tags_query = select(StoreProductTag) \
                .join(StoreProduct) \
                .where(StoreProduct.product_id == product_id)
            tags = self._conn.execute(fetch_tags_query).all()
            return _row_to_product_dto(product, units=units, tags=tags)
        except Exception as exc:
            raise exc
