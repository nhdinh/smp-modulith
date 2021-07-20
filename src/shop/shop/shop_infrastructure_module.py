#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker

from foundation.events import EventBus

from shop.adapter import shop_db
from shop.adapter.queries.catalog_sql_queries import SqlListShopCatalogsQuery
from shop.adapter.queries.product_sql_queries import SqlGetShopProductQuery
from shop.adapter.queries.supplier_sql_queries import SqlListShopProductsBySupplierQuery, SqlListShopSuppliersQuery
from shop.application.queries.catalog_queries import ListShopCatalogsQuery
from shop.application.queries.product_queries import GetShopProductQuery
from shop.application.queries.supplier_queries import ListShopProductsBySupplierQuery, ListShopSuppliersQuery
from shop.application.services.shop_unit_of_work import ShopUnitOfWork


class ShopInfrastructureModule(injector.Module):
    @injector.provider
    def store_db(self) -> shop_db:
        return shop_db

    @injector.provider
    def get_uow(self, conn: Connection, event_bus: EventBus) -> ShopUnitOfWork:
        sessfactory = sessionmaker(bind=conn)
        return ShopUnitOfWork(sessionfactory=sessfactory, event_bus=event_bus)

    # @injector.provider
    # def fetch_store_settings_query(self, conn: Connection) -> ListShopSettingsQuery:
    #     return ListShopSettingsQuery(conn)

    # @injector.provider
    # def fetch_store_address_query(self, conn: Connection) -> ListStoreAddressesQuery:
    #     return SqlListStoreAddressesQuery(conn)

    # @injector.provider
    # def fetch_store_warehouses_query(self, conn: Connection) -> ListStoreWarehousesQuery:
    #     return SqlListStoreWarehousesQuery(conn)
    #
    # @injector.provider
    # def count_store_owner_by_email_query(self, conn: Connection) -> CountStoreOwnerByEmailQuery:
    #     return SqlCountStoreOwnerByEmailQuery(conn)
    #
    @injector.provider
    def list_shop_catalogs_query(self, conn: Connection) -> ListShopCatalogsQuery:
        return SqlListShopCatalogsQuery(conn)

    # @injector.provider
    # def fetch_store_collections_query(self, conn: Connection) -> ListStoreCollectionsQuery:
    #     return SqlListStoreCollectionsQuery(conn)
    #
    # @injector.provider
    # def fetch_products_from_collection_query(self, conn: Connection) -> ListProductsFromCollectionQuery:
    #     return SqlListProductsFromCollectionQuery(conn)
    #
    # @injector.provider
    # def list_product_query(self, conn: Connection) -> ListProductsQuery:
    #     return SqlListProductsQuery(conn)
    #
    @injector.provider
    def get_product_by_id_query(self, conn: Connection) -> GetShopProductQuery:
        return SqlGetShopProductQuery(conn)

    # @injector.provider
    # def list_products_in_catalog(self, conn: Connection) -> ListStoreProductsByCatalogQuery:
    #     return SqlListStoreProductsByCatalogQuery(conn)
    #
    # @injector.provider
    # def list_products_in_store(self, conn: Connection) -> ListStoreProductsQuery:
    #     return SqlListStoreProductsQuery(conn)

    @injector.provider
    def list_suppliers_in_store(self, conn: Connection) -> ListShopSuppliersQuery:
        return SqlListShopSuppliersQuery(conn)

    @injector.provider
    def list_products_by_suppliers(self, conn: Connection) -> ListShopProductsBySupplierQuery:
        return SqlListShopProductsBySupplierQuery(conn)
