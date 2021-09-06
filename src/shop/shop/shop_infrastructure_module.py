#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker

from foundation.events import EventBus
from shop.adapter import shop_db
from shop.adapter.queries.catalog_sql_queries import SqlListShopCatalogsQuery, SqlListShopProductsByCatalogQuery, \
    SqlListAllShopCatalogsQuery, SqlListAllShopCollectionsByCatalogQuery, SqlGetCollectionCacheHashQuery
from shop.adapter.queries.product_sql_queries import SqlGetShopProductQuery, SqlListShopProductsQuery, \
    SqlListShopProductPurchasePricesQuery, SqlListShopSuppliersByProductQuery, SqlListUnitsByShopProductQuery, \
    SqlGetShopProductPurchasePriceQuery, SqlGetShopProductLowestPurchasePriceQuery
from shop.adapter.queries.brand_sql_queries import SqlListShopBrandsQuery, SqlListAllShopBrandsQuery, \
    SqlGetBrandsCacheHashQuery
from shop.adapter.queries.shop_sql_queries import SqlListShopAddressesQuery, SqlGetShopInfoQuery
from shop.adapter.queries.supplier_sql_queries import SqlListShopProductsBySupplierQuery, SqlListShopSuppliersQuery
from shop.application.queries.catalog_queries import ListShopCatalogsQuery, ListShopProductsByCatalogQuery, \
    ListActiveShopCatalogsQuery, ListActiveShopCollectionsByCatalogQuery, GetCollectionCacheHashQuery
from shop.application.queries.product_queries import GetShopProductQuery, ListShopProductsQuery, \
    ListShopProductPurchasePricesQuery, ListShopSuppliersByProductQuery, ListUnitsByShopProductQuery, \
    GetShopProductPurchasePriceQuery, GetShopProductLowestPurchasePriceQuery
from shop.application.queries.brand_queries import ListShopBrandsQuery, ListActiveShopBrandsQuery, \
    GetBrandsCacheHashQuery
from shop.application.queries.shop_queries import ListShopAddressesQuery, GetShopInfoQuery
from shop.application.queries.supplier_queries import ListShopProductsBySupplierQuery, ListShopSuppliersQuery
from shop.application.services.shop_unit_of_work import ShopUnitOfWork
from shop.application.services.shop_user_counters import ShopUserCounter


class ShopInfrastructureModule(injector.Module):
    @injector.provider
    def store_db(self) -> shop_db:
        return shop_db

    @injector.provider
    def get_uow(self, conn: Connection, event_bus: EventBus) -> ShopUnitOfWork:
        sessfactory = sessionmaker(bind=conn)
        return ShopUnitOfWork(sessionfactory=sessfactory, event_bus=event_bus)

    @injector.provider
    def get_shop_user_counter(self, connection: Connection) -> ShopUserCounter:
        return ShopUserCounter(connection)

    @injector.provider
    def get_shop_info_query(self, conn: Connection) -> GetShopInfoQuery:
        return SqlGetShopInfoQuery(conn)

    # @injector.provider
    # def fetch_store_settings_query(self, conn: Connection) -> ListShopSettingsQuery:
    #     return ListShopSettingsQuery(conn)

    @injector.provider
    def list_shop_addresses_query(self, conn: Connection) -> ListShopAddressesQuery:
        return SqlListShopAddressesQuery(conn)

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

    @injector.provider
    def list_active_shop_catalogs_query(self, conn: Connection) -> ListActiveShopCatalogsQuery:
        return SqlListAllShopCatalogsQuery(conn)

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
    def get_product_query(self, conn: Connection) -> GetShopProductQuery:
        return SqlGetShopProductQuery(conn)

    @injector.provider
    def list_products_by_catalog_query(self, conn: Connection) -> ListShopProductsByCatalogQuery:
        return SqlListShopProductsByCatalogQuery(conn)

    @injector.provider
    def list_shop_products_query(self, conn: Connection) -> ListShopProductsQuery:
        return SqlListShopProductsQuery(conn)

    @injector.provider
    def list_shop_suppliers_query(self, conn: Connection) -> ListShopSuppliersQuery:
        return SqlListShopSuppliersQuery(conn)

    @injector.provider
    def list_products_by_suppliers_query(self, conn: Connection) -> ListShopProductsBySupplierQuery:
        return SqlListShopProductsBySupplierQuery(conn)

    @injector.provider
    def list_shop_product_purchase_prices_query(self, conn: Connection) -> ListShopProductPurchasePricesQuery:
        return SqlListShopProductPurchasePricesQuery(conn)

    @injector.provider
    def list_shop_suppliers_by_product(self, conn: Connection) -> ListShopSuppliersByProductQuery:
        return SqlListShopSuppliersByProductQuery(conn)

    @injector.provider
    def list_units_by_shop_product(self, conn: Connection) -> ListUnitsByShopProductQuery:
        return SqlListUnitsByShopProductQuery(conn)

    @injector.provider
    def get_shop_product_purchase_price(self, conn: Connection) -> GetShopProductPurchasePriceQuery:
        return SqlGetShopProductPurchasePriceQuery(conn)

    @injector.provider
    def get_shop_product_lowest_purchase_price(self, conn: Connection) -> GetShopProductLowestPurchasePriceQuery:
        return SqlGetShopProductLowestPurchasePriceQuery(conn)

    @injector.provider
    def list_shop_brands(self, conn: Connection) -> ListShopBrandsQuery:
        return SqlListShopBrandsQuery(conn)

    @injector.provider
    def list_active_shop_brands(self, conn: Connection) -> ListActiveShopBrandsQuery:
        return SqlListAllShopBrandsQuery(conn)

    @injector.provider
    def get_shop_brands_hash(self, conn: Connection) -> GetBrandsCacheHashQuery:
        return SqlGetBrandsCacheHashQuery(conn)

    @injector.provider
    def list_active_shop_collections(self, conn: Connection) -> ListActiveShopCollectionsByCatalogQuery:
        return SqlListAllShopCollectionsByCatalogQuery(conn)

    @injector.provider
    def get_shop_collection_hash(self, conn: Connection) -> GetCollectionCacheHashQuery:
        return SqlGetCollectionCacheHashQuery(conn)
