#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List

from sqlalchemy import select, and_

from db_infrastructure import SqlQuery
from store.adapter.queries.query_common import sql_get_store_id_by_owner, \
    sql_count_products_in_collection, sql_count_collections_in_catalog, \
    sql_count_catalogs_in_store, sql_count_products_in_store, sql_count_suppliers_in_store
from store.adapter.queries.query_factories import list_store_product_query_factory, get_product_query_factory, \
    store_catalog_query_factory
from store.adapter.store_db import store_catalog_table, store_collection_table
from store.application.queries.dto_factories import _row_to_store_settings_dto, _row_to_store_info_dto, \
    _row_to_warehouse_dto, \
    _row_to_address_dto
from store.application.queries.dtos.store_catalog_dto import StoreCatalogResponseDto, _row_to_catalog_dto
from store.application.queries.dtos.store_collection_dto import _row_to_collection_dto
from store.application.queries.dtos.store_product_dto import StoreProductCompactedDto, StoreProductDto, \
    _row_to_product_dto
from store.application.queries.dtos.store_supplier_dto import _row_to_supplier_dto, StoreSupplierDto
from store.application.queries.response_dtos import StoreInfoResponseDto, StoreWarehouseResponseDto, \
    StoreAddressResponseDto
from store.application.queries.store_queries import ListProductsFromCollectionQuery, ListStoreCollectionsQuery, \
    ListStoreCatalogsQuery, \
    ListProductsQuery, \
    GetProductByIdQuery, ListStoreProductsQuery, ListStoreProductsByCatalogQuery, \
    ListStoreWarehousesQuery, ListStoreAddressesQuery, ListStoreSuppliersQuery
from store.application.queries.store_queries import ListStoreSettingsQuery, CountStoreOwnerByEmailQuery
from store.application.usecases.const import ExceptionMessages, ThingGoneInBackHoleError
from store.domain.entities.setting import Setting
from store.domain.entities.store import Store
from store.domain.entities.store_address import StoreAddress
from store.domain.entities.store_catalog import StoreCatalog
from store.domain.entities.store_collection import StoreCollection
from store.domain.entities.store_owner import StoreOwner
from store.domain.entities.store_product import StoreProduct, StoreProductId
from store.domain.entities.store_product_brand import StoreProductBrand
from store.domain.entities.store_product_tag import StoreProductTag
from store.domain.entities.store_supplier import StoreSupplier
from store.domain.entities.store_unit import StoreProductUnit
from store.domain.entities.store_warehouse import StoreWarehouse
from store.domain.entities.value_objects import StoreCatalogId, StoreCollectionId
from web_app.serialization.dto import PaginationOutputDto, AuthorizedPaginationInputDto, paginate_response_factory


class SqlListStoreSettingsQuery(ListStoreSettingsQuery, SqlQuery):
    def query(self, store_of: str) -> StoreInfoResponseDto:
        store_query = select(Store) \
            .join(StoreOwner).where(StoreOwner.email == store_of)

        store_row_proxy = self._conn.execute(store_query).first()
        if not store_row_proxy:
            raise ThingGoneInBackHoleError(ExceptionMessages.STORE_NOT_FOUND)

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


class SqlListProductsFromCollectionQuery(ListProductsFromCollectionQuery, SqlQuery):
    def query(
            self,
            collection_id: StoreCollectionId,
            catalog_id: StoreCatalogId,
            dto: AuthorizedPaginationInputDto
    ) -> PaginationOutputDto[StoreProductCompactedDto]:
        try:
            try:
                current_page = int(dto.page) if int(dto.page) > 0 else 1
                page_size = int(dto.page_size) if int(dto.page_size) > 0 else 10
            except:
                current_page = 1
                page_size = 10

            # get store_id and collection_id
            store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)
            if not store_id:
                raise ThingGoneInBackHoleError(ExceptionMessages.STORE_NOT_FOUND)

            # count products in collection
            product_in_collection_count = sql_count_products_in_collection(collection_reference=collection_id,
                                                                           catalog_reference=catalog_id,
                                                                           store_id=store_id,
                                                                           conn=self._conn)

            fetch_products_query = select([
                StoreProduct,
                StoreCollection.title.label('collection_display_name'),
                StoreCatalog.title.label('catalog_display_name'),
                StoreProductBrand.title.label('brand_display_name'),
            ]) \
                .join(StoreCollection, StoreProduct.collection_id == StoreCollection.collection_id) \
                .join(StoreCatalog, StoreProduct.catalog_id == StoreCatalog.catalog_id) \
                .join(Store, StoreProduct.store_id == Store.store_id) \
                .join(StoreProductBrand, and_(StoreProduct.brand_reference == StoreProductBrand.reference,
                                              Store.store_id == StoreProductBrand.store_id), isouter=True) \
                .where(and_(StoreCollection.reference == collection_id,
                            StoreCatalog.reference == catalog_id,
                            Store.store_id == store_id
                            )) \
                .limit(page_size).offset((current_page - 1) * page_size)

            products = self._conn.execute(fetch_products_query).all()

            return paginate_response_factory(
                current_page=current_page,
                page_size=page_size,
                total_items=product_in_collection_count,
                items=[
                    _row_to_product_dto(row, compacted=True) for row in products
                ]
            )
        except Exception as exc:
            raise exc


class SqlListStoreCatalogsQuery(ListStoreCatalogsQuery, SqlQuery):
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreCatalogResponseDto]:
        try:
            try:
                current_page = int(dto.page) if int(dto.page) > 0 else 1
                page_size = int(dto.page_size) if int(dto.page_size) > 0 else 10
            except:
                current_page = 1
                page_size = 10

            store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)
            if not store_id:
                raise ThingGoneInBackHoleError(ExceptionMessages.STORE_NOT_FOUND)

            # count number of catalogs of this store
            catalog_count = sql_count_catalogs_in_store(store_id=store_id, conn=self._conn)
            if not catalog_count:
                return paginate_response_factory(
                    current_page=dto.page,
                    page_size=dto.page_size,
                    total_items=catalog_count,
                    items=[]
                )

            # get all catalogs limit by page and offset
            fetch_catalogs_query = store_catalog_query_factory(store_id=store_id) \
                .order_by(store_catalog_table.c.created_at) \
                .limit(dto.page_size).offset((current_page - 1) * dto.page_size)

            catalogs = self._conn.execute(fetch_catalogs_query).all()

            # else, continue to load collection
            catalog_indices = set()
            for catalog in catalogs:
                catalog_indices.add(catalog.catalog_id)

            # get all collection with catalog_id in the list of catalog_indices
            collection_query = select([
                store_collection_table,
                store_collection_table.c.disabled.label('is_collection_disabled')
            ]).join(store_catalog_table, store_catalog_table.c.catalog_id == store_collection_table.c.catalog_id) \
                .where(and_(store_catalog_table.c.catalog_id.in_(catalog_indices),
                            store_catalog_table.c.store_id == store_id))

            collections = self._conn.execute(collection_query).all()

            return paginate_response_factory(
                current_page=dto.page,
                page_size=page_size,
                total_items=catalog_count,
                items=[
                    _row_to_catalog_dto(row, collections=[c for c in collections if c.catalog_id == row.catalog_id])
                    for row in catalogs]
            )
        except Exception as exc:
            raise exc


class SqlListStoreCollectionsQuery(ListStoreCollectionsQuery, SqlQuery):
    def query(self, catalog_id: StoreCatalogId, dto: AuthorizedPaginationInputDto):
        try:
            try:
                current_page = int(dto.page) if int(dto.page) > 0 else 1
                page_size = int(dto.page_size) if int(dto.page_size) > 0 else 10
            except:
                current_page = 1
                page_size = 10

            store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)
            if not store_id:
                raise ThingGoneInBackHoleError(ExceptionMessages.STORE_NOT_FOUND)

            collection_count = sql_count_collections_in_catalog(store_id=store_id,
                                                                catalog_id=catalog_id,
                                                                conn=self._conn)

            collection_query = select(store_collection_table) \
                .where(and_(
                store_collection_table.c.store_id == store_id,
                store_collection_table.c.catalog_id == catalog_id
            ))

            collections = self._conn.execute(collection_query).all()
            return paginate_response_factory(
                current_page=current_page,
                page_size=page_size,
                total_items=collection_count,
                items=[
                    _row_to_collection_dto(row) for row in collections
                ]
            )
        except Exception as exc:
            raise exc


class SqlGetProductByIdQuery(GetProductByIdQuery, SqlQuery):
    def query(self,
              owner_email: str,
              product_id: StoreProductId):
        try:
            store_id = sql_get_store_id_by_owner(store_owner=owner_email, conn=self._conn)
            if not store_id:
                raise ThingGoneInBackHoleError(ExceptionMessages.STORE_NOT_FOUND)

            # get the product by id
            query = get_product_query_factory(product_id=product_id)
            product = self._conn.execute(query).first()

            if product:
                fetch_collections_query = select([StoreCollection,
                                                  StoreCollection.disabled.label('is_collection_disabled')]) \
                    .join(StoreProduct, StoreCollection._products).where(StoreProduct.product_id == product_id)
                collections = self._conn.execute(fetch_collections_query).all()

                fetch_units_query = select(StoreProductUnit) \
                    .join(StoreProduct) \
                    .where(StoreProduct.product_id == product_id)
                units = self._conn.execute(fetch_units_query).all()

                fetch_tags_query = select(StoreProductTag) \
                    .join(StoreProduct) \
                    .where(StoreProduct.product_id == product_id)
                tags = self._conn.execute(fetch_tags_query).all()
                return _row_to_product_dto(product, unit_rows=units, tag_rows=tags, collection_rows=collections)
            else:
                raise ThingGoneInBackHoleError(ExceptionMessages.STORE_PRODUCT_NOT_FOUND)
        except Exception as exc:
            raise exc


class SqlListStoreProductsByCatalogQuery(ListStoreProductsByCatalogQuery, SqlQuery):
    def query(self, catalog_id: StoreCatalogId, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[
        StoreProductCompactedDto]:
        try:
            try:
                current_page = int(dto.page) if int(dto.page) > 0 else 1
                page_size = int(dto.page_size) if int(dto.page_size) > 0 else 10
            except:
                current_page = 1
                page_size = 10

            store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)
            if not store_id:
                raise ThingGoneInBackHoleError(ExceptionMessages.STORE_NOT_FOUND)

            # get product counts
            product_counts = sql_count_products_in_store(store_id=store_id, conn=self._conn)

            # build product query
            query = list_store_product_query_factory(store_id=store_id)
            query = query.where(StoreCatalog.catalog_id == catalog_id)
            query = query.limit(page_size).offset((current_page - 1) * page_size)

            # query products
            products = self._conn.execute(query).all()

            return paginate_response_factory(
                current_page=current_page,
                page_size=page_size,
                total_items=product_counts,
                items=[
                    _row_to_product_dto(row, compacted=True) for row in products
                ]
            )

        except Exception as exc:
            raise exc


class SqlListProductsQuery(ListProductsQuery, SqlQuery):
    def query(self,
              owner_email: str,
              catalog_id: StoreCatalogId
              ) -> StoreProductDto:
        try:
            store_id = sql_get_store_id_by_owner(store_owner=owner_email, conn=self._conn)
            if not store_id:
                raise ThingGoneInBackHoleError(ExceptionMessages.STORE_NOT_FOUND)

            query = list_store_product_query_factory(store_id=store_id)
            query = query.where(
                store_catalog_table.c.catalog_id == catalog_id)

            product = self._conn.execute(query).first()

            # TODO: Xem laij
            return product
        except Exception as exc:
            raise exc


class SqlListStoreProductsQuery(ListStoreProductsQuery, SqlQuery):
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreProductCompactedDto]:
        try:
            try:
                current_page = int(dto.page) if int(dto.page) > 0 else 1
                page_size = int(dto.page_size) if int(dto.page_size) > 0 else 10
            except:
                current_page = 1
                page_size = 10

            store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)
            if not store_id:
                raise ThingGoneInBackHoleError(ExceptionMessages.STORE_NOT_FOUND)

            # get product counts
            total_product_cnt = sql_count_products_in_store(store_id=store_id, conn=self._conn)

            # build product query
            query = list_store_product_query_factory(store_id=store_id)
            query = query.limit(page_size).offset((current_page - 1) * page_size)

            # query products
            products = self._conn.execute(query).all()

            return paginate_response_factory(
                current_page=current_page,
                page_size=page_size,
                total_items=total_product_cnt,
                items=[
                    _row_to_product_dto(row, compacted=True) for row in products
                ]
            )
        except Exception as exc:
            raise exc


class SqlListStoreWarehousesQuery(ListStoreWarehousesQuery, SqlQuery):
    def query(self, warehouse_owner: str) -> List[StoreWarehouseResponseDto]:
        store_id = sql_get_store_id_by_owner(store_owner=warehouse_owner, conn=self._conn)
        if not store_id:
            raise ThingGoneInBackHoleError(ExceptionMessages.STORE_NOT_FOUND)

        query = select(StoreWarehouse).join(Store).where(Store.store_id == store_id)  # type:ignore

        warehouses = self._conn.execute(query)
        return [_row_to_warehouse_dto(row) for row in warehouses]


class SqlListStoreAddressesQuery(ListStoreAddressesQuery, SqlQuery):
    def query(self, store_owner: str) -> List[StoreAddressResponseDto]:
        store_id = sql_get_store_id_by_owner(store_owner=store_owner, conn=self._conn)
        if not store_id:
            raise ThingGoneInBackHoleError(ExceptionMessages.STORE_NOT_FOUND)

        query = select(StoreAddress).join(Store, StoreAddress._store).where(Store.store_id == store_id)

        addresses = self._conn.execute(query).all()

        return [_row_to_address_dto(row) for row in addresses]


class SqlListStoreSuppliersQuery(ListStoreSuppliersQuery, SqlQuery):
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreSupplierDto]:
        try:
            try:
                current_page = int(dto.page) if int(dto.page) > 0 else 1
                page_size = int(dto.page_size) if int(dto.page_size) > 0 else 10
            except:
                current_page = 1
                page_size = 10

            store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)
            if not store_id:
                raise ThingGoneInBackHoleError(ExceptionMessages.STORE_NOT_FOUND)

            # get supplier counts
            count_suppliers = sql_count_suppliers_in_store(store_id=store_id, conn=self._conn)

            # build supplier query
            query = select(StoreSupplier).join(Store).where(Store.store_id == store_id)
            query = query.limit(page_size).offset((current_page - 1) * page_size)

            # query products
            suppliers = self._conn.execute(query).all()

            return paginate_response_factory(
                current_page=current_page,
                page_size=page_size,
                total_items=count_suppliers,
                items=[
                    _row_to_supplier_dto(row) for row in suppliers
                ]
            )
        except Exception as exc:
            raise exc
