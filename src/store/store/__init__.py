#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker
from typing import Type

from foundation.events import EventBus, AsyncHandler, AsyncEventHandlerProvider
from store.adapter import store_db
from store.adapter.queries import SqlFetchAllStoreCatalogsQuery, SqlFetchAllStoreCollectionsQuery
from store.adapter.sql_store_queries import SqlFetchStoreSettingsQuery, SqlCountStoreOwnerByEmailQuery
from store.application.queries.store_queries import FetchAllStoreCatalogsQuery, FetchAllStoreCollectionsQuery
from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.services.user_counter_services import UserCounters
from store.application.store_handler_facade import StoreHandlerFacade, StoreCatalogCreatedEventHandler, \
    StoreCollectionCreatedEventHandler, StoreCatalogDeletedEventHandler
from store.application.store_queries import FetchStoreSettingsQuery, CountStoreOwnerByEmailQuery
from store.application.store_repository import SqlAlchemyStoreRepository
from store.application.usecases.catalog.create_store_catalog_uc import CreatingStoreCatalogResponseBoundary, \
    CreateStoreCatalogUC
from store.application.usecases.catalog.invalidate_store_catalog_cache_uc import InvalidateStoreCatalogCacheUC
from store.application.usecases.catalog.remove_store_catalog_uc import RemoveStoreCatalogUC, \
    RemovingStoreCatalogResponseBoundary
from store.application.usecases.catalog.toggle_store_catalog_uc import ToggleStoreCatalogUC
from store.application.usecases.catalog.update_store_catalog_uc import UpdatingStoreCatalogResponseBoundary
from store.application.usecases.collections.create_store_collection_uc import CreateStoreCollectionUC, \
    CreatingStoreCollectionResponseBoundary
from store.application.usecases.collections.toggle_store_collection_uc import ToggleStoreCollectionUC
from store.application.usecases.collections.update_store_collection_uc import UpdatingStoreCollectionResponseBoundary
from store.application.usecases.initialize.confirm_store_registration_uc import \
    ConfirmingStoreRegistrationResponseBoundary, \
    ConfirmStoreRegistrationUC
from store.application.usecases.initialize.register_store_uc import RegisterStoreUC, RegisteringStoreResponseBoundary
from store.application.usecases.manage.add_store_manager import AddStoreManagerUC, AddingStoreManagerResponseBoundary
from store.application.usecases.manage.update_store_settings_uc import UpdateStoreSettingsUC, \
    UpdatingStoreSettingsResponseBoundary
from store.application.usecases.store_uc_common import GenericStoreResponseBoundary
from store.domain.events.store_catalog_events import StoreCatalogCreatedEvent, StoreCollectionCreatedEvent, \
    StoreCatalogDeletedEvent
from store.domain.events.store_created_event import StoreCreatedEvent
from store.domain.events.store_registered_event import StoreRegisteredEvent, StoreRegistrationConfirmedEvent

__all__ = [
    'StoreRegisteredEvent', 'StoreRegistrationConfirmedEvent', 'StoreCreatedEvent'
]


class StoreModule(injector.Module):
    @injector.provider
    def register_store_uc(self, boundary: RegisteringStoreResponseBoundary, uow: StoreUnitOfWork,
                          user_counter_services: UserCounters) -> RegisterStoreUC:
        return RegisterStoreUC(boundary, uow, user_counter_services)

    @injector.provider
    def confirm_store_registration_uc(self, boundary: ConfirmingStoreRegistrationResponseBoundary,
                                      uow: StoreUnitOfWork) -> ConfirmStoreRegistrationUC:
        return ConfirmStoreRegistrationUC(boundary, uow)

    @injector.provider
    def add_store_manager_uc(self, boundary: AddingStoreManagerResponseBoundary,
                             uow: StoreUnitOfWork) -> AddStoreManagerUC:
        return AddStoreManagerUC(boundary, uow)

    @injector.provider
    def update_store_settings_uc(self, boundary: UpdatingStoreSettingsResponseBoundary,
                                 uow: StoreUnitOfWork) -> UpdateStoreSettingsUC:
        return UpdateStoreSettingsUC(boundary, uow)

    @injector.provider
    def invalidate_store_catalog_cache_uc(self, boundary: GenericStoreResponseBoundary,
                                          uow: StoreUnitOfWork) -> InvalidateStoreCatalogCacheUC:
        return InvalidateStoreCatalogCacheUC(boundary, uow)

    """
    STORE CATALOG OPERATIONS
    """

    @injector.provider
    def create_store_catalog_uc(self, boundary: CreatingStoreCatalogResponseBoundary,
                                uow: StoreUnitOfWork) -> CreateStoreCatalogUC:
        return CreateStoreCatalogUC(boundary, uow)

    @injector.provider
    def toggle_store_catalog_uc(self, boundary: UpdatingStoreCatalogResponseBoundary,
                                uow: StoreUnitOfWork) -> ToggleStoreCatalogUC:
        return ToggleStoreCatalogUC(boundary, uow)

    @injector.provider
    def remove_store_catalog_uc(self, boundary: RemovingStoreCatalogResponseBoundary,
                                uow: StoreUnitOfWork) -> RemoveStoreCatalogUC:
        return RemoveStoreCatalogUC(boundary, uow)

    """
    STORE COLLECTION OPERATIONS
    """

    @injector.provider
    def create_store_collection_uc(self, boundary: CreatingStoreCollectionResponseBoundary,
                                   uow: StoreUnitOfWork) -> CreateStoreCollectionUC:
        return CreateStoreCollectionUC(boundary, uow)

    @injector.provider
    def toggle_store_collection_uc(self, boundary: UpdatingStoreCollectionResponseBoundary,
                                   uow: StoreUnitOfWork) -> ToggleStoreCollectionUC:
        return ToggleStoreCollectionUC(boundary, uow)

    @injector.provider
    def facade(self, connection: Connection) -> StoreHandlerFacade:
        return StoreHandlerFacade(connection=connection)

    def async_bind(self, binder: injector.Binder, event: Type, handler: Type) -> None:
        # shorthand for multibind
        binder.multibind(AsyncHandler[event], to=AsyncEventHandlerProvider(handler))

    def configure(self, binder: injector.Binder) -> None:
        # binder.multibind(AsyncHandler[StoreCreatedEvent], to=AsyncEventHandlerProvider(StoreCreatedEventHandler))

        self.async_bind(binder, StoreCatalogCreatedEvent, StoreCatalogCreatedEventHandler)
        self.async_bind(binder, StoreCatalogDeletedEvent, StoreCatalogDeletedEventHandler)

        self.async_bind(binder, StoreCollectionCreatedEvent, StoreCollectionCreatedEventHandler)


class StoreInfrastructureModule(injector.Module):
    @injector.provider
    def store_db(self) -> store_db:
        return store_db

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
    def fetch_store_settings_query(self, conn: Connection) -> FetchStoreSettingsQuery:
        return SqlFetchStoreSettingsQuery(conn)

    @injector.provider
    def count_store_owner_by_email_query(self, conn: Connection) -> CountStoreOwnerByEmailQuery:
        return SqlCountStoreOwnerByEmailQuery(conn)

    @injector.provider
    def fetch_store_catalogs_query(self, conn: Connection) -> FetchAllStoreCatalogsQuery:
        return SqlFetchAllStoreCatalogsQuery(conn)

    @injector.provider
    def fetch_store_collections_query(self, conn: Connection) -> FetchAllStoreCollectionsQuery:
        return SqlFetchAllStoreCollectionsQuery(conn)
