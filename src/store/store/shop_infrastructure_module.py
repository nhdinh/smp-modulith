#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker

from foundation.events import EventBus

from store import ShopUnitOfWork
from store.adapter import shop_db
from store.adapter.queries.sql_get_shop_product_query import SqlGetShopProductQuery
from store.adapter.queries.sql_store_queries import (
    SqlCountStoreOwnerByEmailQuery,
    SqlListProductsFromCollectionQuery,
    SqlListProductsQuery,
    SqlListShopCatalogsQuery,
    SqlListStoreAddressesQuery,
    SqlListStoreCollectionsQuery,
    SqlListStoreProductsByCatalogQuery,
    SqlListStoreProductsQuery,
    SqlListStoreSettingsQuery,
    SqlListStoreSuppliersQuery,
    SqlListStoreWarehousesQuery,
)
from store.application.queries.get_shop_product_query import GetShopProductQuery
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
from store.application.services.user_counter_services import UserCounters


class ShopInfrastructureModule(injector.Module):
    @injector.provider
    def get_user_counter_services(self, conn: Connection) -> UserCounters:
        return UserCounters(conn=conn)

    @injector.provider
    def fetch_store_settings_query(self, conn: Connection) -> ListStoreSettingsQuery:
        return SqlListStoreSettingsQuery(conn)

    @injector.provider
    def fetch_store_address_query(self, conn: Connection) -> ListStoreAddressesQuery:
        return SqlListStoreAddressesQuery(conn)

    @injector.provider
    def fetch_store_warehouses_query(self, conn: Connection) -> ListStoreWarehousesQuery:
        return SqlListStoreWarehousesQuery(conn)

    @injector.provider
    def count_store_owner_by_email_query(self, conn: Connection) -> CountStoreOwnerByEmailQuery:
        return SqlCountStoreOwnerByEmailQuery(conn)

    @injector.provider
    def fetch_store_catalogs_query(self, conn: Connection) -> ListShopCatalogsQuery:
        return SqlListShopCatalogsQuery(conn)

    @injector.provider
    def fetch_store_collections_query(self, conn: Connection) -> ListStoreCollectionsQuery:
        return SqlListStoreCollectionsQuery(conn)

    @injector.provider
    def fetch_products_from_collection_query(self, conn: Connection) -> ListProductsFromCollectionQuery:
        return SqlListProductsFromCollectionQuery(conn)