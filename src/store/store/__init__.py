#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Type

import injector
from minio import Minio
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker

from foundation.events import EventBus, AsyncHandler, AsyncEventHandlerProvider
from foundation.fs import FileSystem
from store.adapter import shop_db
from store.adapter.queries.sql_store_queries import SqlListStoreSettingsQuery, SqlCountStoreOwnerByEmailQuery, \
    SqlListProductsFromCollectionQuery, SqlListStoreCollectionsQuery, SqlListStoreCatalogsQuery, \
    SqlListProductsQuery, SqlGetStoreProductQuery, SqlListStoreProductsQuery, \
    SqlListStoreProductsByCatalogQuery, SqlListStoreWarehousesQuery, SqlListStoreAddressesQuery, \
    SqlListStoreSuppliersQuery
from store.application.queries.store_queries import ListStoreCatalogsQuery, ListStoreCollectionsQuery, \
    ListProductsFromCollectionQuery, ListProductsQuery, GetStoreProductQuery, ListStoreProductsQuery, \
    ListStoreProductsByCatalogQuery, ListStoreWarehousesQuery, ListStoreAddressesQuery, ListStoreSuppliersQuery
from store.application.queries.store_queries import ListStoreSettingsQuery, CountStoreOwnerByEmailQuery
from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.services.user_counter_services import UserCounters
from store.application.store_handler_facade import StoreHandlerFacade, StoreCatalogDeletedEventHandler, \
    StoreProductCreatedOrUpdatedEventHandler
from store.application.shop_repository import SqlAlchemyShopRepository
from store.application.usecases.catalog.create_store_catalog_uc import AddingShopCatalogResponseBoundary, \
    AddShopCatalogUC
from store.application.usecases.catalog.invalidate_store_catalog_cache_uc import InvalidateStoreCatalogCacheUC
from store.application.usecases.catalog.remove_store_catalog_uc import RemoveStoreCatalogUC, \
    RemovingStoreCatalogResponseBoundary
from store.application.usecases.catalog.systemize_store_catalog_uc import SystemizeStoreCatalogUC
from store.application.usecases.catalog.toggle_store_catalog_uc import ToggleStoreCatalogUC
from store.application.usecases.catalog.update_store_catalog_uc import UpdatingStoreCatalogResponseBoundary, \
    UpdateStoreCatalogUC
from store.application.usecases.collection.create_store_collection_uc import CreateStoreCollectionUC, \
    CreatingStoreCollectionResponseBoundary
from store.application.usecases.collection.make_store_collection_default_uc import MakeStoreCollectionDefaultUC
from store.application.usecases.collection.toggle_store_collection_uc import ToggleStoreCollectionUC
from store.application.usecases.collection.update_store_collection_uc import UpdatingStoreCollectionResponseBoundary, \
    UpdateStoreCollectionUC
from store.application.usecases.create_store_warehouse_uc import CreatingStoreWarehouseResponseBoundary, \
    CreateStoreWarehouseUC
from store.application.usecases.initialize.confirm_store_registration_uc import \
    ConfirmingStoreRegistrationResponseBoundary, \
    ConfirmStoreRegistrationUC
from store.application.usecases.initialize.register_shop_uc import RegisterShopUC, RegisteringShopResponseBoundary
from store.application.usecases.manage.add_store_manager import AddStoreManagerUC, AddingStoreManagerResponseBoundary
from store.application.usecases.manage.create_store_address_uc import CreatingStoreAddressResponseBoundary, \
    CreateStoreAddressUC
from store.application.usecases.manage.resend_store_registration_confirmation_uc import \
    ResendingRegistrationConfirmationResponseBoundary, ResendRegistrationConfirmationUC
from store.application.usecases.manage.update_store_settings_uc import UpdateStoreSettingsUC, \
    UpdatingStoreSettingsResponseBoundary
from store.application.usecases.manage.upload_image_uc import UploadImageUC, UploadingImageResponseBoundary
from store.application.usecases.product.create_store_product_uc import CreatingStoreProductResponseBoundary, \
    CreateStoreProductUC
from store.application.usecases.product.remove_store_product_attribute_uc import RemoveStoreProductAttributeUC, \
    RemovingStoreProductAttributeResponseBoundary
from store.application.usecases.product.remove_store_product_uc import RemoveStoreProductUC, \
    RemovingStoreProductResponseBoundary
from store.application.usecases.product.update_store_product_uc import UpdateStoreProductUC, \
    UpdatingStoreProductResponseBoundary
from store.application.usecases.store_uc_common import GenericStoreResponseBoundary
from store.domain.entities.collision import CollionCreatedEvent, CollionCreatedEventHandler
from store.domain.events.store_catalog_events import StoreCatalogCreatedEvent, StoreCollectionCreatedEvent, \
    StoreCatalogDeletedEvent
from store.domain.events.store_created_event import StoreCreatedEvent
from store.domain.events.store_product_events import StoreProductCreatedEvent, StoreProductUpdatedEvent
from store.domain.events.shop_registered_event import ShopRegisteredEvent, ShopRegistrationConfirmedEvent


class StoreModule(injector.Module):
    @injector.provider
    def register_store_uc(self, boundary: RegisteringShopResponseBoundary, uow: StoreUnitOfWork,
                          user_counter_services: UserCounters) -> RegisterShopUC:
        return RegisterShopUC(boundary, uow, user_counter_services)

    @injector.provider
    def confirm_store_registration_uc(self, boundary: ConfirmingStoreRegistrationResponseBoundary,
                                      uow: StoreUnitOfWork) -> ConfirmStoreRegistrationUC:
        return ConfirmStoreRegistrationUC(boundary, uow)

    @injector.provider
    def resend_store_registration_uc(self, boundary: ResendingRegistrationConfirmationResponseBoundary,
                                     uow: StoreUnitOfWork) -> ResendRegistrationConfirmationUC:
        return ResendRegistrationConfirmationUC(boundary, uow)

    @injector.provider
    def add_store_manager_uc(self, boundary: AddingStoreManagerResponseBoundary,
                             uow: StoreUnitOfWork) -> AddStoreManagerUC:
        return AddStoreManagerUC(boundary, uow)

    @injector.provider
    def create_store_address_uc(self, boundary: CreatingStoreAddressResponseBoundary,
                                uow: StoreUnitOfWork) -> CreateStoreAddressUC:
        return CreateStoreAddressUC(boundary, uow)

    @injector.provider
    def update_store_settings_uc(self, boundary: UpdatingStoreSettingsResponseBoundary,
                                 uow: StoreUnitOfWork) -> UpdateStoreSettingsUC:
        return UpdateStoreSettingsUC(boundary, uow)

    @injector.provider
    def create_store_warehouse_uc(self, boundary: CreatingStoreWarehouseResponseBoundary,
                                  uow: StoreUnitOfWork) -> CreateStoreWarehouseUC:
        return CreateStoreWarehouseUC(boundary, uow)

    @injector.provider
    def invalidate_store_catalog_cache_uc(self, boundary: GenericStoreResponseBoundary,
                                          uow: StoreUnitOfWork) -> InvalidateStoreCatalogCacheUC:
        return InvalidateStoreCatalogCacheUC(boundary, uow)

    @injector.provider
    def upload_image_uc(self, boundary: UploadingImageResponseBoundary, uow: StoreUnitOfWork,
                        minio_client: Minio, fs: FileSystem) -> UploadImageUC:
        return UploadImageUC(boundary, uow, minio_client, fs)

    # region ## StoreCatalog Operations ##

    @injector.provider
    def create_store_catalog_uc(self, boundary: AddingShopCatalogResponseBoundary,
                                uow: StoreUnitOfWork) -> AddShopCatalogUC:
        return AddShopCatalogUC(boundary, uow)

    @injector.provider
    def toggle_store_catalog_uc(self, boundary: UpdatingStoreCatalogResponseBoundary,
                                uow: StoreUnitOfWork) -> ToggleStoreCatalogUC:
        return ToggleStoreCatalogUC(boundary, uow)

    @injector.provider
    def remove_store_catalog_uc(self, boundary: RemovingStoreCatalogResponseBoundary,
                                uow: StoreUnitOfWork) -> RemoveStoreCatalogUC:
        return RemoveStoreCatalogUC(boundary, uow)

    @injector.provider
    def update_store_catalog_uc(self, boundary: UpdatingStoreCatalogResponseBoundary,
                                uow: StoreUnitOfWork) -> UpdateStoreCatalogUC:
        return UpdateStoreCatalogUC(boundary, uow)

    @injector.provider
    def make_store_catalog_system_uc(self, boundary: UpdatingStoreCatalogResponseBoundary,
                                     uow: StoreUnitOfWork) -> SystemizeStoreCatalogUC:
        return SystemizeStoreCatalogUC(boundary, uow)

    # endregion

    # region ## StoreCollection Operations ##

    @injector.provider
    def create_store_collection_uc(self, boundary: CreatingStoreCollectionResponseBoundary,
                                   uow: StoreUnitOfWork) -> CreateStoreCollectionUC:
        return CreateStoreCollectionUC(boundary, uow)

    @injector.provider
    def update_store_collection_uc(self, boundary: UpdatingStoreCollectionResponseBoundary,
                                   uow: StoreUnitOfWork) -> UpdateStoreCollectionUC:
        return UpdateStoreCollectionUC(boundary, uow)

    @injector.provider
    def toggle_store_collection_uc(self, boundary: UpdatingStoreCollectionResponseBoundary,
                                   uow: StoreUnitOfWork) -> ToggleStoreCollectionUC:
        return ToggleStoreCollectionUC(boundary, uow)

    @injector.provider
    def make_store_collection_default_uc(self, boundary: UpdatingStoreCollectionResponseBoundary,
                                         uow: StoreUnitOfWork) -> MakeStoreCollectionDefaultUC:
        return MakeStoreCollectionDefaultUC(boundary, uow)

    # endregion

    # region ## StoreProduct Operation ##

    @injector.provider
    def create_store_product_uc(self, boundary: CreatingStoreProductResponseBoundary,
                                uow: StoreUnitOfWork) -> CreateStoreProductUC:
        return CreateStoreProductUC(boundary, uow)

    @injector.provider
    def update_store_product_uc(self, boundary: UpdatingStoreProductResponseBoundary,
                                uow: StoreUnitOfWork, fs: FileSystem) -> UpdateStoreProductUC:
        return UpdateStoreProductUC(boundary, uow, fs)

    @injector.provider
    def remove_store_product_uc(self, boundary: RemovingStoreProductResponseBoundary,
                                uow: StoreUnitOfWork, fs: FileSystem) -> RemoveStoreProductUC:
        return RemoveStoreProductUC(boundary, uow, fs)

    @injector.provider
    def remove_store_product_attribute_uc(self, boundary: RemovingStoreProductAttributeResponseBoundary,
                                          uow: StoreUnitOfWork, fs: FileSystem) -> RemoveStoreProductAttributeUC:
        return RemoveStoreProductAttributeUC(boundary, uow, fs)

    # endregion

    # region ## StoreHandlers Facade and configuration for event listening ##

    @injector.provider
    def facade(self, connection: Connection) -> StoreHandlerFacade:
        return StoreHandlerFacade(connection=connection)

    def async_bind(self, binder: injector.Binder, event: Type, handler: Type) -> None:
        # shorthand for multi-bind
        binder.multibind(AsyncHandler[event], to=AsyncEventHandlerProvider(handler))

    def configure(self, binder: injector.Binder) -> None:
        # binder.multibind(AsyncHandler[StoreCreatedEvent], to=AsyncEventHandlerProvider(StoreCreatedEventHandler))

        # self.async_bind(binder, StoreCatalogCreatedEvent, StoreCatalogCreatedEventHandler)
        self.async_bind(binder, StoreCatalogDeletedEvent, StoreCatalogDeletedEventHandler)

        # self.async_bind(binder, StoreCollectionCreatedEvent, StoreCollectionCreatedEventHandler)
        self.async_bind(binder, StoreProductCreatedEvent, StoreProductCreatedOrUpdatedEventHandler)
        self.async_bind(binder, StoreProductUpdatedEvent, StoreProductCreatedOrUpdatedEventHandler)
        self.async_bind(binder, CollionCreatedEvent, CollionCreatedEventHandler)

    # endregion


class StoreInfrastructureModule(injector.Module):
    @injector.provider
    def store_db(self) -> shop_db:
        return shop_db

    @injector.provider
    def get_uow(self, conn: Connection, event_bus: EventBus) -> StoreUnitOfWork:
        sessfactory = sessionmaker(bind=conn)
        return StoreUnitOfWork(sessionfactory=sessfactory, event_bus=event_bus)

    # @injector.provider
    # def get_repository(self, uow: StoreUnitOfWork) -> SqlAlchemyStoreRepository:
    #     return SqlAlchemyStoreRepository(session=uow.session)

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
    def fetch_store_catalogs_query(self, conn: Connection) -> ListStoreCatalogsQuery:
        return SqlListStoreCatalogsQuery(conn)

    @injector.provider
    def fetch_store_collections_query(self, conn: Connection) -> ListStoreCollectionsQuery:
        return SqlListStoreCollectionsQuery(conn)

    @injector.provider
    def fetch_products_from_collection_query(self, conn: Connection) -> ListProductsFromCollectionQuery:
        return SqlListProductsFromCollectionQuery(conn)

    @injector.provider
    def list_product_query(self, conn: Connection) -> ListProductsQuery:
        return SqlListProductsQuery(conn)

    @injector.provider
    def get_product_by_id_query(self, conn: Connection) -> GetStoreProductQuery:
        return SqlGetStoreProductQuery(conn)

    @injector.provider
    def list_products_in_catalog(self, conn: Connection) -> ListStoreProductsByCatalogQuery:
        return SqlListStoreProductsByCatalogQuery(conn)

    @injector.provider
    def list_products_in_store(self, conn: Connection) -> ListStoreProductsQuery:
        return SqlListStoreProductsQuery(conn)

    @injector.provider
    def list_suppliers_in_store(self, conn: Connection) -> ListStoreSuppliersQuery:
        return SqlListStoreSuppliersQuery(conn)


__all__ = [
    StoreModule, StoreInfrastructureModule,
    'ShopRegisteredEvent', 'ShopRegistrationConfirmedEvent', 'StoreCreatedEvent'
]
