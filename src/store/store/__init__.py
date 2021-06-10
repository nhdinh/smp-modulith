#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker

from foundation.events import EventBus, AsyncHandler, AsyncEventHandlerProvider
from store.adapter.queries import SqlFetchAllStoreCatalogsQuery
from store.application.queries.store_queries import FetchAllStoreCatalogsQuery
from store.application.store_handler_facade import StoreHandlerFacade, StoreCatalogCreatedEventHandler
from store.application.usecases.manage.add_store_manager import AddStoreManagerUC, AddingStoreManagerResponseBoundary
from store.application.usecases.initialize.confirm_store_registration_uc import ConfirmingStoreRegistrationResponseBoundary, \
    ConfirmStoreRegistrationUC
from store.application.usecases.catalog.create_store_catalog_uc import CreatingStoreCatalogResponseBoundary, \
    CreateStoreCatalogUC
from store.application.usecases.catalog.invalidate_store_catalog_cache_uc import InvalidateStoreCatalogCacheUC
from store.application.usecases.store_uc_common import GenericStoreResponseBoundary
from store.application.usecases.manage.update_store_settings_uc import UpdateStoreSettingsUC, \
    UpdatingStoreSettingsResponseBoundary
from store.domain.events.store_catalog_events import StoreCatalogCreatedEvent
from store.domain.events.store_created_successfully_event import StoreCreatedSuccessfullyEvent
from store.domain.events.store_registered_event import StoreRegisteredEvent, StoreRegistrationConfirmedEvent
from store.adapter import store_db
from store.adapter.sql_store_queries import SqlFetchStoreSettingsQuery, SqlCountStoreOwnerByEmailQuery
from store.application.services.store_unit_of_work import StoreUnitOfWork
from store.application.services.user_counter_services import UserCounters
from store.application.store_queries import FetchStoreSettingsQuery, CountStoreOwnerByEmailQuery
from store.application.store_repository import SqlAlchemyStoreRepository
from store.application.usecases.initialize.register_store_uc import RegisterStoreUC, RegisteringStoreResponseBoundary

__all__ = [
    'StoreRegisteredEvent', 'StoreRegistrationConfirmedEvent', 'StoreCreatedSuccessfullyEvent'
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
    def create_store_catalog_uc(self, boundary: CreatingStoreCatalogResponseBoundary,
                                uow: StoreUnitOfWork) -> CreateStoreCatalogUC:
        return CreateStoreCatalogUC(boundary, uow)

    @injector.provider
    def invalidate_store_catalog_cache_uc(self, boundary: GenericStoreResponseBoundary,
                                          uow: StoreUnitOfWork) -> InvalidateStoreCatalogCacheUC:
        return InvalidateStoreCatalogCacheUC(boundary, uow)

    @injector.provider
    def facade(self, connection: Connection) -> StoreHandlerFacade:
        return StoreHandlerFacade(connection=connection)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[StoreCatalogCreatedEvent],
                         to=AsyncEventHandlerProvider(StoreCatalogCreatedEventHandler))


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
    def fetchall_store_catalogs_query(self, conn: Connection) -> FetchAllStoreCatalogsQuery:
        return SqlFetchAllStoreCatalogsQuery(conn)
