#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List

from sqlalchemy import and_, select

from db_infrastructure import SqlQuery
from store.adapter.queries.query_common import (
    sql_count_catalogs_in_store,
    sql_count_collections_in_catalog,
    sql_count_products_in_collection,
    sql_count_products_in_store,
    sql_count_suppliers_in_store,
    sql_get_store_id_by_owner,
    sql_verify_shop_id_with_partner_id,
)
from store.adapter.queries.query_factories import (
    get_store_query_factory,
    list_store_product_query_factory,
    store_catalog_query_factory,
)
from store.adapter.shop_db import (
    shop_addresses_table,
    shop_catalog_table,
    shop_collection_table,
    shop_settings_table,
    shop_table,
    shop_warehouse_table,
)
from store.application.queries.dto_factories import (
    _row_to_address_dto,
    _row_to_store_info_dto,
    _row_to_store_settings_dto,
    _row_to_warehouse_dto,
)
from store.application.queries.dtos.store_catalog_dto import StoreCatalogResponseDto, _row_to_catalog_dto
from store.application.queries.dtos.store_collection_dto import _row_to_collection_dto
from store.application.queries.dtos.store_product_dto import (
    StoreProductCompactedDto,
    StoreProductDto,
    _row_to_product_dto,
)
from store.application.queries.dtos.store_supplier_dto import StoreSupplierDto, _row_to_supplier_dto
from store.application.queries.response_dtos import (
    StoreAddressResponseDto,
    StoreInfoResponseDto,
    StoreWarehouseResponseDto,
)
from store.application.queries.store_queries import (
    CountStoreOwnerByEmailQuery,
    ListProductsFromCollectionQuery,
    ListProductsQuery,
    ListShopCatalogsQuery,
    ListStoreAddressesQuery,
    ListStoreCollectionsQuery,
    ListStoreProductsByCatalogQuery,
    ListStoreProductsQuery,
    ListStoreSettingsQuery,
    ListStoreSuppliersQuery,
    ListStoreWarehousesQuery,
)
from store.application.usecases.const import ExceptionMessages, ThingGoneInBlackHoleError
from store.domain.entities.shop import Shop
from store.domain.entities.shop_catalog import ShopCatalog
from store.domain.entities.shop_supplier import ShopSupplier
from store.domain.entities.store_collection import ShopCollection
from store.domain.entities.store_product import ShopProduct
from store.domain.entities.store_product_brand import ShopProductBrand
from store.domain.entities.value_objects import ShopCatalogId, StoreCollectionId
from web_app.serialization.dto import AuthorizedPaginationInputDto, PaginationOutputDto, paginate_response_factory


class SqlListStoreSettingsQuery(ListStoreSettingsQuery, SqlQuery):
    def query(self, store_owner_email: str) -> StoreInfoResponseDto:
        store_row_proxy = self._conn.execute(get_store_query_factory(store_owner_email=store_owner_email)).first()
        if not store_row_proxy:
            raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_NOT_FOUND)

        # make StoreInfoResponseDto
        store_dto = _row_to_store_info_dto(store_row_proxy)

        query = select(shop_settings_table) \
            .where(shop_settings_table.c.shop_id == store_dto.shop_id)

        rows = self._conn.execute(query).all()

        # build settings[]
        for row in rows:
            store_dto.settings.append(_row_to_store_settings_dto(row))

        # return the dto
        return store_dto


class SqlCountStoreOwnerByEmailQuery(CountStoreOwnerByEmailQuery, SqlQuery):
    def query(self, email: str) -> int:
        raise NotImplementedError


class SqlListProductsFromCollectionQuery(ListProductsFromCollectionQuery, SqlQuery):
    def query(
            self,
            collection_id: StoreCollectionId,
            catalog_id: ShopCatalogId,
            dto: AuthorizedPaginationInputDto
    ) -> PaginationOutputDto[StoreProductCompactedDto]:
        try:
            # get store_id and collection_id
            store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)
            if not store_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_NOT_FOUND)

            # count products in collection
            product_in_collection_count = sql_count_products_in_collection(collection_reference=collection_id,
                                                                           catalog_reference=catalog_id,
                                                                           store_id=store_id,
                                                                           conn=self._conn)

            fetch_products_query = select([
                ShopProduct,
                ShopCollection.title.label('collection_display_name'),
                ShopCatalog.title.label('catalog_display_name'),
                ShopProductBrand.title.label('brand_display_name'),
            ]) \
                .join(ShopCollection, ShopProduct.collection_id == ShopCollection.collection_id) \
                .join(ShopCatalog, ShopProduct.catalog_id == ShopCatalog.catalog_id) \
                .join(Shop, ShopProduct.shop_id == Shop.shop_id) \
                .join(ShopProductBrand, and_(ShopProduct.brand_reference == ShopProductBrand.reference,
                                             Shop.shop_id == ShopProductBrand.shop_id), isouter=True) \
                .where(and_(ShopCollection.reference == collection_id,
                            ShopCatalog.reference == catalog_id,
                            Shop.shop_id == store_id
                            )) \
                .limit(dto.page_size).offset((dto.current_page - 1) * dto.page_size)

            products = self._conn.execute(fetch_products_query).all()

            return paginate_response_factory(
                input_dto=dto,
                total_items=product_in_collection_count,
                items=[
                    _row_to_product_dto(row, compacted=True) for row in products
                ]
            )
        except Exception as exc:
            raise exc





class SqlListStoreCollectionsQuery(ListStoreCollectionsQuery, SqlQuery):
    def query(self, catalog_id: ShopCatalogId, dto: AuthorizedPaginationInputDto):
        try:
            store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)
            if not store_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_NOT_FOUND)

            collection_count = sql_count_collections_in_catalog(store_id=store_id,
                                                                catalog_id=catalog_id,
                                                                conn=self._conn)

            collection_query = select([
                shop_collection_table,
                shop_collection_table.c.disabled.label('is_collection_disabled')
            ]) \
                .where(and_(
                shop_collection_table.c.shop_id == store_id,
                shop_collection_table.c.catalog_id == catalog_id
            ))

            collections = self._conn.execute(collection_query).all()
            return paginate_response_factory(
                input_dto=dto,
                total_items=collection_count,
                items=[
                    _row_to_collection_dto(row) for row in collections
                ]
            )
        except Exception as exc:
            raise exc


class SqlListStoreProductsByCatalogQuery(ListStoreProductsByCatalogQuery, SqlQuery):
    def query(self, catalog_id: ShopCatalogId, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[
        StoreProductCompactedDto]:
        try:
            store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)
            if not store_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_NOT_FOUND)

            # get product counts
            product_counts = sql_count_products_in_store(store_id=store_id, conn=self._conn)

            # build product query
            query = list_store_product_query_factory(store_id=store_id)
            query = query.where(ShopCatalog.catalog_id == catalog_id)
            query = query.limit(dto.page_size).offset((dto.current_page - 1) * dto.page_size)

            # query products
            products = self._conn.execute(query).all()

            return paginate_response_factory(
                input_dto=dto,
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
              catalog_id: ShopCatalogId
              ) -> StoreProductDto:
        try:
            store_id = sql_get_store_id_by_owner(store_owner=owner_email, conn=self._conn)
            if not store_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_NOT_FOUND)

            query = list_store_product_query_factory(store_id=store_id)
            query = query.where(
                shop_catalog_table.c.catalog_id == catalog_id)

            product = self._conn.execute(query).first()

            # TODO: Xem laij
            return product
        except Exception as exc:
            raise exc


class SqlListStoreProductsQuery(ListStoreProductsQuery, SqlQuery):
    def query(self, dto: AuthorizedPaginationInputDto) -> PaginationOutputDto[StoreProductCompactedDto]:
        try:
            store_id = sql_get_store_id_by_owner(store_owner=dto.current_user, conn=self._conn)
            if not store_id:
                raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_NOT_FOUND)

            # get product counts
            total_product_cnt = sql_count_products_in_store(store_id=store_id, conn=self._conn)

            # build product query
            query = list_store_product_query_factory(store_id=store_id)
            query = query.limit(dto.page_size).offset((dto.current_page - 1) * dto.page_size)

            # query products
            products = self._conn.execute(query).all()

            return paginate_response_factory(
                input_dto=dto,
                total_items=total_product_cnt,
                items=[
                    _row_to_product_dto(row) for row in products
                ]
            )
        except Exception as exc:
            raise exc


class SqlListStoreWarehousesQuery(ListStoreWarehousesQuery, SqlQuery):
    def query(self, warehouse_owner: str) -> List[StoreWarehouseResponseDto]:
        store_id = sql_get_store_id_by_owner(store_owner=warehouse_owner, conn=self._conn)
        if not store_id:
            raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_NOT_FOUND)

        query = select(shop_warehouse_table).where(shop_warehouse_table.c.shop_id == store_id)  # type:ignore

        warehouses = self._conn.execute(query)
        return [_row_to_warehouse_dto(row) for row in warehouses]


class SqlListStoreAddressesQuery(ListStoreAddressesQuery, SqlQuery):
    def query(self, store_owner: str) -> List[StoreAddressResponseDto]:
        store_id = sql_get_store_id_by_owner(store_owner=store_owner, conn=self._conn)
        if not store_id:
            raise ThingGoneInBlackHoleError(ExceptionMessages.SHOP_NOT_FOUND)

        # query = select(StoreAddress).join(Store, StoreAddress._store).where(Store.shop_id == store_id)
        query = select(shop_addresses_table).join(shop_table,
                                                  shop_addresses_table.c.shop_id == shop_table.c.shop_id).where(
            shop_table.c.shop_id == store_id)

        addresses = self._conn.execute(query).all()

        return [_row_to_address_dto(row) for row in addresses]